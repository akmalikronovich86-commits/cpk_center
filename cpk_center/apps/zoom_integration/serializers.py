from rest_framework import serializers

from .models import ZoomMeeting, ZoomRecording


class ZoomRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoomRecording
        fields = [
            'id', 'recording_url', 'download_url',
            'duration_seconds', 'file_size_mb',
            'recording_type', 'created_at'
        ]


class ZoomMeetingSerializer(serializers.ModelSerializer):
    recordings = ZoomRecordingSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = ZoomMeeting
        fields = [
            'id', 'topic', 'teacher', 'teacher_name',
            'course', 'course_name', 'schedule',
            'zoom_meeting_id', 'zoom_join_url', 'zoom_start_url',
            'zoom_password', 'start_time', 'duration',
            'recurrence', 'status',
            'waiting_room', 'join_before_host',
            'mute_upon_entry', 'auto_recording',
            'started_at', 'ended_at',
            'created_at', 'updated_at',
            'recordings',
        ]
        read_only_fields = [
            'zoom_meeting_id', 'zoom_join_url', 'zoom_start_url',
            'zoom_password', 'started_at', 'ended_at',
        ]
