"""Сервисный слой модуля аттестации.

Здесь сосредоточена вся бизнес-логика расчёта посещаемости, результатов
экзамена, проверки допуска, назначения пересдачи и утверждения сертификата.
Views и admin вызывают только эти функции, чтобы логика оставалась единой.
"""
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone


def _q2(value):
    """Округление до 2 знаков после запятой (Decimal)."""
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_or_create_record(student, group):
    """Возвращает (или создаёт) AssessmentRecord для пары слушатель/группа."""
    from .models import AssessmentRecord
    record, _created = AssessmentRecord.objects.get_or_create(
        student=student, group=group
    )
    return record


def calculate_attendance(student, group, save=True, record=None):
    """Рассчитывает посещаемость слушателя по группе и обновляет запись.

    Логика зачёта посещения (на уровне модели Attendance.counted_value):
      * полное присутствие -> 1.0
      * опоздание/присутствие > 50% занятия -> 0.5
      * присутствие <= 50% -> 0.0
    Порог: (сумма зачтённых посещений) / (число занятий) >= 70%.
    """
    from apps.schedules.models import Attendance, Schedule

    from .models import AssessmentRecord

    if record is None:
        record = get_or_create_record(student, group)

    lessons = Schedule.objects.filter(group=group)
    total_lessons = lessons.count()

    counted = Decimal('0')
    attendances = Attendance.objects.filter(
        schedule__group=group, student=student
    ).select_related('schedule')
    for att in attendances:
        counted += Decimal(str(att.counted_value))

    if total_lessons > 0:
        percentage = (counted / Decimal(total_lessons)) * Decimal('100')
    else:
        percentage = Decimal('0')

    record.total_lessons = total_lessons
    record.counted_attendances = _q2(counted)
    record.attendance_percentage = _q2(percentage)
    record.attendance_passed = percentage >= Decimal(AssessmentRecord.ATTENDANCE_THRESHOLD)

    if save:
        record.save()
    return record


def calculate_exam_result(student, group, save=True, record=None):
    """Рассчитывает результат экзамена (и пересдачи) по данным TestSession.

    Основная попытка — сессия с ``is_retake=False`` (берётся лучший результат),
    пересдача — сессия с ``is_retake=True``. Порог сдачи — 70%.
    """
    from apps.exams.models import TestSession

    from .models import AssessmentRecord

    if record is None:
        record = get_or_create_record(student, group)
    course = group.course

    sessions = TestSession.objects.filter(
        student=student, course=course, is_completed=True
    )

    main_sessions = sessions.filter(is_retake=False)
    retake_sessions = sessions.filter(is_retake=True)

    # Основной экзамен — лучший процент среди основных попыток
    exam_score = None
    for s in main_sessions:
        pct = Decimal(str(s.score_percentage))
        if exam_score is None or pct > exam_score:
            exam_score = pct

    # Пересдача — лучший процент среди пересдач
    retake_score = None
    for s in retake_sessions:
        pct = Decimal(str(s.score_percentage))
        if retake_score is None or pct > retake_score:
            retake_score = pct

    threshold = Decimal(AssessmentRecord.EXAM_THRESHOLD)

    record.exam_score = _q2(exam_score) if exam_score is not None else None
    record.exam_passed = exam_score is not None and exam_score >= threshold
    record.retake_score = _q2(retake_score) if retake_score is not None else None
    record.retake_passed = retake_score is not None and retake_score >= threshold

    if save:
        record.save()
    return record


def check_eligibility(student, group, recalculate=True, save=True):
    """Проверяет допуск слушателя к сертификату.

    Условие допуска: посещаемость >= 70% И экзамен сдан (основной или пересдача).
    При ``recalculate=True`` предварительно пересчитывает посещаемость и экзамен.
    """
    record = get_or_create_record(student, group)
    if recalculate:
        calculate_attendance(student, group, save=False, record=record)
        calculate_exam_result(student, group, save=False, record=record)

    record.eligible_for_certificate = bool(
        record.attendance_passed and record.final_exam_passed
    )
    if save:
        record.save()
    return record


def recalculate_record(student, group):
    """Полный пересчёт записи: посещаемость + экзамен + допуск (одно сохранение)."""
    return check_eligibility(student, group, recalculate=True, save=True)


def allow_retake(student, group, director):
    """Директор разрешает пересдачу экзамена слушателю."""
    record = get_or_create_record(student, group)
    record.retake_allowed = True
    record.retake_allowed_by = director
    record.retake_allowed_at = timezone.now()
    record.save(update_fields=[
        'retake_allowed', 'retake_allowed_by', 'retake_allowed_at', 'updated_at'
    ])
    return record


@transaction.atomic
def approve_certificate(student, group, director):
    """Директор утверждает сертификат и инициирует его выдачу.

    Возвращает кортеж (record, certificate). Если слушатель не допущен,
    выбрасывает ValueError.
    """
    from apps.certificates.models import Certificate
    from apps.groups.models import StudentRecord

    record = recalculate_record(student, group)

    if not record.eligible_for_certificate:
        raise ValueError(
            'Слушатель не допущен к сертификату: не выполнены условия '
            'по посещаемости и/или экзамену.'
        )

    # Находим/создаём карточку слушателя (Certificate.student -> StudentRecord)
    student_record, _created = StudentRecord.objects.get_or_create(
        user=student,
        defaults={
            'full_name': student.get_full_name() or student.username,
        },
    )

    course = group.course

    # Не создаём дубликат, если сертификат уже связан
    certificate = record.certificate
    if certificate is None:
        certificate = Certificate.objects.filter(
            student=student_record, course=course
        ).exclude(status='revoked').first()

    if certificate is None:
        certificate = Certificate.objects.create(
            student=student_record,
            course=course,
            status='issued',
            created_by=director,
        )
    else:
        if certificate.status == 'draft':
            certificate.status = 'issued'
            certificate.save(update_fields=['status', 'updated_at'])

    record.certificate = certificate
    record.certificate_approved = True
    record.certificate_approved_by = director
    record.certificate_approved_at = timezone.now()
    record.save(update_fields=[
        'certificate', 'certificate_approved', 'certificate_approved_by',
        'certificate_approved_at', 'updated_at',
    ])

    return record, certificate
