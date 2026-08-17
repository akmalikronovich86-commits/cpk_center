from import_export import resources
from .models import (
    StudentReport, CertificateReport, ScheduleReport, LecturerReport,
)


class StudentReportResource(resources.ModelResource):
    class Meta:
        model = StudentReport
        fields = (
            'id', 'full_name_qualification', 'group', 'phone_number',
            'position', 'regional_branch', 'final_grade',
            'independent_study_topic', 'qualification_period',
        )
        export_order = fields


class CertificateReportResource(resources.ModelResource):
    class Meta:
        model = CertificateReport
        fields = (
            'id', 'certificate_number', 'series', 'issue_date',
            'expiry_date', 'status', 'registry_number', 'qr_code',
        )
        export_order = fields


class ScheduleReportResource(resources.ModelResource):
    class Meta:
        model = ScheduleReport
        fields = ('id', 'date', 'start_time', 'end_time', 'status')
        export_order = fields


class LecturerReportResource(resources.ModelResource):
    class Meta:
        model = LecturerReport
        fields = ('id', 'experience_years', 'specialization')
        export_order = fields
