from django.contrib import admin
from .models import (
    StudentReport, CertificateReport, ScheduleReport, LecturerReport,
)


@admin.register(StudentReport)
class StudentReportAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    search_fields = ('id',)


@admin.register(CertificateReport)
class CertificateReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'certificate_number', 'status', 'issue_date')
    search_fields = ('certificate_number',)
    list_filter = ('status',)


@admin.register(ScheduleReport)
class ScheduleReportAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    search_fields = ('id',)


@admin.register(LecturerReport)
class LecturerReportAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
