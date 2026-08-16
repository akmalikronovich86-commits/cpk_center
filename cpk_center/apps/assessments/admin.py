from django.contrib import admin

from . import services
from .models import AssessmentRecord


@admin.register(AssessmentRecord)
class AssessmentRecordAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'group', 'attendance_percentage', 'attendance_passed',
        'exam_score', 'exam_passed', 'retake_allowed', 'retake_passed',
        'eligible_for_certificate', 'certificate_approved',
    )
    list_filter = (
        'attendance_passed', 'exam_passed', 'retake_allowed', 'retake_passed',
        'eligible_for_certificate', 'certificate_approved', 'group',
    )
    search_fields = (
        'student__username', 'student__first_name', 'student__last_name',
        'student__full_name', 'group__name',
    )
    autocomplete_fields = ()
    readonly_fields = (
        'attendance_percentage', 'counted_attendances', 'total_lessons',
        'created_at', 'updated_at', 'certificate_approved_at', 'retake_allowed_at',
    )
    actions = ['action_recalculate', 'action_allow_retake', 'action_approve_certificate']

    @admin.action(description='Пересчитать посещаемость и экзамен')
    def action_recalculate(self, request, queryset):
        count = 0
        for record in queryset:
            services.recalculate_record(record.student, record.group)
            count += 1
        self.message_user(request, f'Пересчитано записей: {count}')

    @admin.action(description='Разрешить пересдачу')
    def action_allow_retake(self, request, queryset):
        count = 0
        for record in queryset:
            services.allow_retake(record.student, record.group, request.user)
            count += 1
        self.message_user(request, f'Пересдача разрешена для {count} слушателей')

    @admin.action(description='Утвердить сертификат (для допущенных)')
    def action_approve_certificate(self, request, queryset):
        approved, skipped = 0, 0
        for record in queryset:
            try:
                services.approve_certificate(record.student, record.group, request.user)
                approved += 1
            except ValueError:
                skipped += 1
        self.message_user(
            request,
            f'Утверждено сертификатов: {approved}. Пропущено (не допущены): {skipped}.'
        )
