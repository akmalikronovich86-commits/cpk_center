from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.courses.models import AcademicGroup, Course
from apps.groups.models import StudentRecord
from apps.materials.models import Material
from apps.schedules.models import Attendance, Schedule
from apps.users.decorators import lecturer_required
from apps.users.models import User

# ===== НАВИГАЦИЯ =====
PAGES_ORDER = [
    ('lecturers:lecturer_dashboard', 'Bosh sahifa', '🏠'),
    ('lecturers:lecturer_schedule', 'Dars jadvali', '📅'),
    ('lecturers:lecturer_courses', 'Kurslar', '📚'),
    ('lecturers:lecturer_students', 'Tinglovchilar', '👥'),
    ('assessments:teacher_students', 'Attestatsiya', '✅'),
    ('lecturers:lecturer_exam_results', 'Imtihon natijalari', '📝'),
    ('lecturers:lecturer_materials', 'Materiallar', '📄'),
    ('lecturers:lecturer_zoom', 'Zoom uchrashuvlar', '📹'),
]

def get_navigation(current_page_name):
    """Возвращает prev/next для навигации"""
    for i, (url, name, icon) in enumerate(PAGES_ORDER):
        if url == current_page_name:
            prev_page = PAGES_ORDER[i-1] if i > 0 else None
            next_page = PAGES_ORDER[i+1] if i < len(PAGES_ORDER) - 1 else None
            return {
                'current_page_name': name,
                'current_icon': icon,
                'prev_page_url': prev_page[0] if prev_page else None,
                'prev_page_name': prev_page[1] if prev_page else None,
                'next_page_url': next_page[0] if next_page else None,
                'next_page_name': next_page[1] if next_page else None,
            }
    return {}

@login_required
@lecturer_required
def lecturer_dashboard(request):
    """Основной дашборд преподавателя"""
    now = timezone.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)

    # Начало и конец сегодняшнего дня
    today_start = timezone.make_aware(timezone.datetime(today.year, today.month, today.day, 0, 0, 0))
    today_end = timezone.make_aware(timezone.datetime(today.year, today.month, today.day, 23, 59, 59))

    # Начало и конец завтрашнего дня
    tomorrow_start = timezone.make_aware(timezone.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0))
    tomorrow_end = timezone.make_aware(timezone.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59))

    # ===== МОИ ДАННЫЕ =====
    # Мои курсы
    my_courses = Course.objects.filter(lecturer=request.user)
    total_courses = my_courses.count()

    # Мои группы (через курсы)
    my_groups = AcademicGroup.objects.filter(course__lecturer=request.user)
    total_groups = my_groups.count()

    # Мои студенты (через группы - по названию группы)
    my_group_names = my_groups.values_list('name', flat=True)
    my_students = StudentRecord.objects.filter(group__in=my_group_names)
    total_students = my_students.count()

    # Моё расписание - сегодня
    today_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=today_start,
        date_start__lte=today_end
    ).order_by('date_start')[:5]

    # Моё расписание - завтра
    tomorrow_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=tomorrow_start,
        date_start__lte=tomorrow_end
    ).order_by('date_start')[:5]

    # Всего расписаний
    total_schedules = Schedule.objects.filter(lecturer=request.user).count()

    # Мои материалы
    my_materials = Material.objects.filter(uploaded_by=request.user)
    total_materials = my_materials.count()

    # ===== БЛИЖАЙШИЕ ЗАНЯТИЯ =====
    upcoming_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=now
    ).order_by('date_start')[:10]

    context = {
        'today': today,
        'now': now,
        'my_courses': my_courses,
        'total_courses': total_courses,
        'my_groups': my_groups,
        'total_groups': total_groups,
        'total_students': total_students,
        'today_schedules': today_schedules,
        'tomorrow_schedules': tomorrow_schedules,
        'total_schedules': total_schedules,
        'my_materials': my_materials,
        'total_materials': total_materials,
        'upcoming_schedules': upcoming_schedules,
    }

    context.update(get_navigation('lecturers:lecturer_dashboard'))
    return render(request, 'lecturers/dashboard.html', context)

@login_required
@lecturer_required
def lecturer_schedule(request):
    """Моё расписание"""
    now = timezone.now()
    today = now.date()

    # Фильтры
    date_filter = request.GET.get('date')

    schedules = Schedule.objects.filter(lecturer=request.user).select_related(
        'course', 'group'
    ).order_by('date_start')

    if date_filter:
        from datetime import datetime
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            day_start = timezone.make_aware(timezone.datetime(filter_date.year, filter_date.month, filter_date.day, 0, 0, 0))
            day_end = timezone.make_aware(timezone.datetime(filter_date.year, filter_date.month, filter_date.day, 23, 59, 59))
            schedules = schedules.filter(date_start__gte=day_start, date_start__lte=day_end)
        except ValueError:
            pass

    context = {
        'schedules': schedules,
        'today': today,
    }

    context.update(get_navigation('lecturers:lecturer_schedule'))
    return render(request, 'lecturers/schedule.html', context)

@login_required
@lecturer_required
def lecturer_courses(request):
    """Мои курсы"""
    courses = Course.objects.filter(lecturer=request.user)

    context = {
        'courses': courses,
        'total_courses': courses.count(),
    }

    context.update(get_navigation('lecturers:lecturer_courses'))
    return render(request, 'lecturers/courses.html', context)

@login_required
@lecturer_required
def lecturer_students(request):
    """Мои студенты (через группы моих курсов)"""
    my_groups = AcademicGroup.objects.filter(course__lecturer=request.user)
    my_group_names = my_groups.values_list('name', flat=True)

    students = StudentRecord.objects.filter(
        group__in=my_group_names
    ).order_by('full_name')

    # Фильтры
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(full_name__icontains=search) |
            Q(xtm__icontains=search) |
            Q(phone__icontains=search)
        )

    context = {
        'students': students,
        'total_students': students.count(),
        'my_groups': my_groups,
    }

    context.update(get_navigation('lecturers:lecturer_students'))
    return render(request, 'lecturers/students.html', context)

@login_required
@lecturer_required
def lecturer_materials(request):
    """Мои учебные материалы"""
    materials = Material.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')

    context = {
        'materials': materials,
        'total_materials': materials.count(),
    }

    context.update(get_navigation('lecturers:lecturer_materials'))
    return render(request, 'lecturers/materials.html', context)

@login_required
@lecturer_required
def upload_material(request):
    """Загрузка нового материала преподавателем"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        material_type = request.POST.get('material_type', 'document')
        course_id = request.POST.get('course')

        # Получаем курс
        if course_id:
            try:
                course = Course.objects.get(id=course_id, lecturer=request.user)
            except Course.DoesNotExist:
                messages.error(request, "Kurs topilmadi yoki siz bu kursga ma'ruzachi emassiz")
                return redirect('lecturers:upload_material')
        else:
            course = None

        # Обрабатываем файл
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            messages.error(request, "Fayl yuklanmadi. Iltimos, faylni tanlang")
            return redirect('lecturers:upload_material')

        # Создаём материал
        material = Material.objects.create(
            title=title or uploaded_file.name,
            description=description,
            type=material_type,
            course=course,
            uploaded_by=request.user,
            file=uploaded_file,
            is_published=True  # Сразу публикуем
        )

        messages.success(request, f"Material muvaffaqiyatli yuklandi: {material.title}")
        return redirect('lecturers:lecturer_materials')

    # GET запрос - показываем форму
    my_courses = Course.objects.filter(lecturer=request.user)

    context = {
        'my_courses': my_courses,
    }

    return render(request, 'lecturers/upload_material.html', context)



@login_required
@lecturer_required
def lecturer_attendance(request):
    """Просмотр посещаемости (только просмотр)"""
    from datetime import timedelta

    from django.utils import timezone

    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    # Мои занятия за последние 30 дней
    my_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=last_30_days
    ).select_related('course', 'group').order_by('-date_start')

    # Статистика посещаемости
    attendance_stats = []
    for schedule in my_schedules:
        attendances = Attendance.objects.filter(schedule=schedule)
        total = attendances.count()
        present = attendances.filter(status='present').count()
        absent = attendances.filter(status='absent').count()
        late = attendances.filter(status='late').count()

        attendance_stats.append({
            'schedule': schedule,
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'attendance_rate': (present / total * 100) if total > 0 else 0
        })

    context = {
        'attendance_stats': attendance_stats,
        'total_schedules': my_schedules.count(),
    }

    return render(request, 'lecturers/attendance.html', context)


@login_required
@lecturer_required
def lecturer_attendance_detail(request, schedule_id):
    """Детальная посещаемость конкретного занятия с возможностью отметки"""
    schedule = get_object_or_404(Schedule, id=schedule_id, lecturer=request.user)

    # Получаем список студентов группы
    from apps.groups.models import StudentRecord
    group_students = StudentRecord.objects.filter(group=schedule.group.name) if schedule.group else []

    # Получаем существующие отметки посещаемости
    attendances = Attendance.objects.filter(schedule=schedule).select_related('student')

    # Создаём словарь для быстрого доступа к статусам
    attendance_dict = {att.student.id: att for att in attendances}

    # Формируем список студентов с их статусами
    student_attendance_list = []
    for student_record in group_students:
        # Находим User объект по XTM или другому идентификатору
        try:
            user = User.objects.get(username=student_record.xtm)
        except User.DoesNotExist:
            continue

        attendance = attendance_dict.get(user.id)
        student_attendance_list.append({
            'user': user,
            'student_record': student_record,
            'attendance': attendance,
            'status': attendance.status if attendance else 'absent',
        })

    context = {
        'schedule': schedule,
        'student_attendance_list': student_attendance_list,
    }

    return render(request, 'lecturers/attendance_detail.html', context)

@login_required
@lecturer_required
def mark_attendance(request, schedule_id):
    """Сохранение отметок посещаемости преподавателем"""
    if request.method != 'POST':
        return redirect('lecturers:lecturer_attendance_detail', schedule_id=schedule_id)

    schedule = get_object_or_404(Schedule, id=schedule_id, lecturer=request.user)

    # Получаем данные из формы
    student_ids = request.POST.getlist('student_ids[]')

    from apps.assessments.services import calculate_attendance

    updated_count = 0
    for student_id in student_ids:
        status = request.POST.get(f'status_{student_id}')
        if not status:
            continue

        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            continue

        # Создаём или обновляем запись посещаемости
        attendance, created = Attendance.objects.update_or_create(
            schedule=schedule,
            student=student,
            defaults={
                'status': status,
                'marked_by': request.user,
            }
        )
        updated_count += 1

        # Пересчитываем AssessmentRecord для этого студента
        if schedule.group:
            calculate_attendance(student, schedule.group, save=True)

    messages.success(request, f"Davomat belgilandi: {updated_count} ta tinglovchi")
    return redirect('lecturers:lecturer_attendance_detail', schedule_id=schedule_id)


@login_required
@lecturer_required
def lecturer_exam_results(request):
    """Список групп для ввода результатов экзамена"""
    my_groups = AcademicGroup.objects.filter(course__lecturer=request.user).select_related('course')

    context = {
        'groups': my_groups,
        'total_groups': my_groups.count(),
    }

    context.update(get_navigation('lecturers:lecturer_dashboard'))
    return render(request, 'lecturers/exam_results_groups.html', context)


@login_required
@lecturer_required
def lecturer_exam_results_group(request, group_id):
    """Ввод результатов экзамена для группы"""
    group = get_object_or_404(AcademicGroup, id=group_id, course__lecturer=request.user)

    # Получаем студентов группы
    from apps.assessments.models import AssessmentRecord
    from apps.groups.models import StudentRecord

    group_students = StudentRecord.objects.filter(group=group.name)

    # Формируем список студентов с их текущими результатами
    student_results = []
    for student_record in group_students:
        try:
            user = User.objects.get(username=student_record.xtm, role='student')
        except User.DoesNotExist:
            continue

        # Получаем или создаём запись аттестации
        assessment, _ = AssessmentRecord.objects.get_or_create(
            student=user,
            group=group
        )

        student_results.append({
            'user': user,
            'student_record': student_record,
            'assessment': assessment,
        })

    context = {
        'group': group,
        'student_results': student_results,
    }

    return render(request, 'lecturers/exam_results_input.html', context)


@login_required
@lecturer_required
def save_exam_results(request, group_id):
    """Сохранение результатов экзамена"""
    if request.method != 'POST':
        return redirect('lecturers:lecturer_exam_results_group', group_id=group_id)

    group = get_object_or_404(AcademicGroup, id=group_id, course__lecturer=request.user)

    from decimal import Decimal

    from apps.assessments.models import AssessmentRecord
    from apps.assessments.services import check_eligibility

    student_ids = request.POST.getlist('student_ids[]')
    updated_count = 0

    for student_id in student_ids:
        exam_score = request.POST.get(f'exam_score_{student_id}', '').strip()
        retake_score = request.POST.get(f'retake_score_{student_id}', '').strip()

        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            continue

        # Получаем запись аттестации
        assessment, _ = AssessmentRecord.objects.get_or_create(
            student=student,
            group=group
        )

        # Обновляем баллы если введены
        updated = False
        if exam_score:
            try:
                score = Decimal(exam_score)
                if 0 <= score <= 100:
                    assessment.exam_score = score
                    assessment.exam_passed = score >= AssessmentRecord.EXAM_THRESHOLD
                    updated = True
            except (ValueError, Decimal.InvalidOperation):
                pass

        if retake_score:
            try:
                score = Decimal(retake_score)
                if 0 <= score <= 100:
                    assessment.retake_score = score
                    assessment.retake_passed = score >= AssessmentRecord.EXAM_THRESHOLD
                    updated = True
            except (ValueError, Decimal.InvalidOperation):
                pass

        if updated:
            assessment.save()
            # Пересчитываем допуск к сертификату
            check_eligibility(student, group, recalculate=False, save=True)
            updated_count += 1

    messages.success(request, f"Imtihon natijalari saqlandi: {updated_count} ta tinglovchi")
    return redirect('lecturers:lecturer_exam_results_group', group_id=group_id)


@login_required
@lecturer_required
def lecturer_zoom(request):
    """Мои Zoom встречи"""
    try:
        from apps.zoom_integration.models import ZoomMeeting

        meetings = ZoomMeeting.objects.filter(
            teacher=request.user
        ).order_by('-start_time')
    except ImportError:
        meetings = []

    context = {
        'meetings': meetings,
        'total_meetings': meetings.count() if hasattr(meetings, 'count') else 0,
    }

    context.update(get_navigation('lecturers:lecturer_zoom'))
    return render(request, 'lecturers/zoom.html', context)
