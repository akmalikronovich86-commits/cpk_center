from django.contrib import admin
from .models import ZoomAccount, ZoomMeeting, ZoomMeetingParticipant, ZoomRecording


@admin.register(ZoomAccount)
class ZoomAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_id', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'account_id')


@admin.register(ZoomMeeting)
class ZoomMeetingAdmin(admin.ModelAdmin):
    list_display = (
        'topic', 'teacher', 'start_time', 'duration', 
        'status', 'zoom_meeting_id'
    )
    list_filter = ('status', 'recurrence', 'auto_recording')
    search_fields = ('topic', 'zoom_meeting_id', 'teacher__username')
    readonly_fields = (
        'zoom_meeting_id', 'zoom_join_url', 'zoom_start_url',
        'zoom_password', 'created_at', 'updated_at'
    )
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('topic', 'schedule', 'course', 'teacher', 'zoom_account')
        }),
        ('Zoom данные', {
            'fields': (
                'zoom_meeting_id', 'zoom_join_url', 'zoom_start_url',
                'zoom_password'
            )
        }),
        ('Параметры', {
            'fields': (
                'start_time', 'duration', 'recurrence',
                'waiting_room', 'join_before_host', 'mute_upon_entry',
                'auto_recording'
            )
        }),
        ('Статус', {
            'fields': ('status', 'started_at', 'ended_at')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ZoomMeetingParticipant)
class ZoomMeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'meeting', 'join_time', 'duration_minutes')
    list_filter = ('meeting',)
    search_fields = ('full_name', 'email')


@admin.register(ZoomRecording)
class ZoomRecordingAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'recording_type', 'duration_seconds', 'file_size_mb', 'created_at')
    list_filter = ('recording_type',)
