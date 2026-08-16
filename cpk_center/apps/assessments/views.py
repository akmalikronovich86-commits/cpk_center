"""Views модуля аттестации: кабинеты преподавателя, руководителя отдела и Директора."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.courses.models import AcademicGroup, Enrollment
from apps.users.decorators import require_role
from apps.users.models import User

from . import services
from .models import AssessmentRecord


def _group_students(group):
    """Список слушателей группы (по активным зачислениям)."""
    student_ids = Enrollment.objects.filter(
        group=group, is_active=True
    ).values_list('student_id', flat=True)
    return User.objects.filter(id__in=list(student_ids), role='student')


def _sync_group_records(group):
    """Пересчитывает записи аттестации для всех слушателей группы."""
    records = []
    for student in _group_students(group):
        records.append(services.recalculate_record(student, group))
    return records


# ---------------------------------------------------------------------------
# Преподаватель (ma'ruzachi)
# ---------------------------------------------------------------------------
@login_required
@require_role('lecturer')
def teacher_students(request):
    """Список групп и слушателей преподавателя с посещаемостью и статусом."""
    from apps.schedules.models import Schedule

    # Группы, где преподаватель ведёт занятия
    group_ids = Schedule.objects.filter(
        lecturer=request.user
    ).values_list('group_id', flat=True).distinct()
    groups = AcademicGroup.objects.filter(
        id__in=list(group_ids)
    ).select_related('course')

    groups_data = []
    for group in groups:
        records = _sync_group_records(group)
        groups_data.append({'group': group, 'records': records})

    context = {
        'groups_data': groups_data,
        'threshold': AssessmentRecord.ATTENDANCE_THRESHOLD,
    }
    return render(request, 'assessments/teacher_students.html', context)


# ---------------------------------------------------------------------------
# Руководитель учебного отдела (bo'lim boshlig'i)
# ---------------------------------------------------------------------------
@login_required
@require_role('department_head')
def department_report(request):
    """Сводный отчёт по всем учебным группам."""
    groups = AcademicGroup.objects.select_related('course').all()

    groups_summary = []
    total_eligible = 0
    total_students = 0
    for group in groups:
        records = _sync_group_records(group)
        count = len(records)
        eligible = sum(1 for r in records if r.eligible_for_certificate)
        approved = sum(1 for r in records if r.certificate_approved)
        if count:
            avg_attendance = sum(float(r.attendance_percentage) for r in records) / count
        else:
            avg_attendance = 0
        total_eligible += eligible
        total_students += count
        groups_summary.append({
            'group': group,
            'student_count': count,
            'eligible': eligible,
            'approved': approved,
            'avg_attendance': round(avg_attendance, 1),
        })

    context = {
        'groups_summary': groups_summary,
        'total_students': total_students,
        'total_eligible': total_eligible,
        'total_groups': groups.count(),
    }
    return render(request, 'assessments/department_report.html', context)


# ---------------------------------------------------------------------------
# Директор
# ---------------------------------------------------------------------------
@login_required
@require_role('director')
def director_dashboard(request):
    """Дашборд Директора: утверждение сертификатов и назначение пересдач."""

    if request.method == 'POST':
        action = request.POST.get('action')
        record_id = request.POST.get('record_id')
        record = get_object_or_404(AssessmentRecord, id=record_id)

        if action == 'approve_certificate':
            try:
                services.approve_certificate(record.student, record.group, request.user)
                messages.success(
                    request,
                    f'Сертификат для {record.student.get_full_name() or record.student.username} утверждён.'
                )
            except ValueError as exc:
                messages.error(request, str(exc))
        elif action == 'allow_retake':
            services.allow_retake(record.student, record.group, request.user)
            messages.success(
                request,
                f'Пересдача для {record.student.get_full_name() or record.student.username} разрешена.'
            )
        elif action == 'recalculate':
            services.recalculate_record(record.student, record.group)
            messages.info(request, 'Данные пересчитаны.')
        return redirect('assessments:director_dashboard')

    # Актуализируем записи по всем группам перед показом
    for group in AcademicGroup.objects.all():
        _sync_group_records(group)

    ready_for_certificate = AssessmentRecord.objects.filter(
        eligible_for_certificate=True, certificate_approved=False
    ).select_related('student', 'group', 'group__course')

    failed_exam = AssessmentRecord.objects.filter(
        exam_passed=False, retake_passed=False, retake_allowed=False
    ).select_related('student', 'group', 'group__course')

    awaiting_retake = AssessmentRecord.objects.filter(
        retake_allowed=True, retake_passed=False, exam_passed=False
    ).select_related('student', 'group', 'group__course')

    approved = AssessmentRecord.objects.filter(
        certificate_approved=True
    ).select_related('student', 'group', 'group__course')[:20]

    context = {
        'ready_for_certificate': ready_for_certificate,
        'failed_exam': failed_exam,
        'awaiting_retake': awaiting_retake,
        'approved': approved,
        'ready_count': ready_for_certificate.count(),
        'failed_count': failed_exam.count(),
    }
    return render(request, 'assessments/director_dashboard.html', context)
