"""
Proxy-модели для отчётов (таблиц не создают)
"""
from apps.groups.models import StudentRecord
from apps.certificates.models import Certificate
from apps.schedules.models import Schedule
from apps.users.models import LecturerProfile


class StudentReport(StudentRecord):
    class Meta:
        proxy = True
        verbose_name = "Hisobot: Tinglovchilar (Excel)"
        verbose_name_plural = "Hisobot: Tinglovchilar"


class CertificateReport(Certificate):
    class Meta:
        proxy = True
        verbose_name = "Hisobot: Sertifikatlar (Excel)"
        verbose_name_plural = "Hisobot: Sertifikatlar"


class ScheduleReport(Schedule):
    class Meta:
        proxy = True
        verbose_name = "Hisobot: Dars jadvali (Excel)"
        verbose_name_plural = "Hisobot: Dars jadvali"


class LecturerReport(LecturerProfile):
    class Meta:
        proxy = True
        verbose_name = "Hisobot: Ma'ruzachilar (Excel)"
        verbose_name_plural = "Hisobot: Ma'ruzachilar"
