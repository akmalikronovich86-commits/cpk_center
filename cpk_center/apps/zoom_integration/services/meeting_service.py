"""
Сервис для управления встречами Zoom
"""
import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from .zoom_api import ZoomAPIClient

logger = logging.getLogger(__name__)


class MeetingService:
    """Высокоуровневый сервис для работы с встречами"""

    def __init__(self, zoom_account=None):
        self.zoom_account = zoom_account
        self.client = ZoomAPIClient(
            account_id=zoom_account.account_id if zoom_account else None,
            client_id=zoom_account.client_id if zoom_account else None,
            client_secret=zoom_account.client_secret if zoom_account else None,
        )

    def create_meeting_for_schedule(self, schedule, teacher):
        """Создание встречи для занятия из расписания"""
        from ..models import ZoomMeeting

        # Формируем данные для Zoom API
        meeting_data = {
            'topic': f"{schedule.course.name} - {schedule.lesson_topic or 'Dars'}",
            'type': 2,  # Scheduled meeting
            'start_time': schedule.start_time.isoformat(),
            'duration': schedule.duration_minutes or 60,
            'timezone': settings.ZOOM_MEETING_DEFAULTS['timezone'],
            'password': self._generate_password(),
            'settings': {
                'waiting_room': settings.ZOOM_MEETING_DEFAULTS['waiting_room'],
                'join_before_host': settings.ZOOM_MEETING_DEFAULTS['join_before_host'],
                'mute_upon_entry': settings.ZOOM_MEETING_DEFAULTS['mute_upon_entry'],
                'auto_recording': settings.ZOOM_MEETING_DEFAULTS['auto_recording'],
                'watermark': settings.ZOOM_MEETING_DEFAULTS['watermark'],
                'host_video': True,
                'participant_video': False,
                'enforce_login': False,
            }
        }

        # Создаём встречу в Zoom
        zoom_user_id = teacher.zoom_user_id or 'me'
        zoom_response = self.client.create_meeting(zoom_user_id, meeting_data)

        # Сохраняем в БД
        meeting = ZoomMeeting.objects.create(
            schedule=schedule,
            course=schedule.course,
            teacher=teacher,
            zoom_account=self.zoom_account,
            zoom_meeting_id=str(zoom_response['id']),
            zoom_join_url=zoom_response['join_url'],
            zoom_start_url=zoom_response['start_url'],
            zoom_password=meeting_data['password'],
            topic=meeting_data['topic'],
            start_time=schedule.start_time,
            duration=meeting_data['duration'],
        )

        logger.info(f"Zoom meeting created: {meeting.zoom_meeting_id}")
        return meeting

    def start_meeting(self, meeting):
        """Начать встречу"""
        meeting.status = 'live'
        meeting.started_at = timezone.now()
        meeting.save()
        logger.info(f"Meeting started: {meeting.zoom_meeting_id}")

    def end_meeting(self, meeting):
        """Завершить встречу"""
        meeting.status = 'completed'
        meeting.ended_at = timezone.now()
        meeting.save()

        # Получаем записи
        self._sync_recordings(meeting)
        logger.info(f"Meeting ended: {meeting.zoom_meeting_id}")

    def cancel_meeting(self, meeting):
        """Отменить встречу"""
        try:
            self.client.delete_meeting(meeting.zoom_meeting_id)
        except Exception as e:
            logger.error(f"Error deleting Zoom meeting: {e}")

        meeting.status = 'cancelled'
        meeting.save()

    def sync_meetings(self, teacher):
        """Синхронизация встреч с Zoom"""
        from ..models import ZoomMeeting

        zoom_user_id = teacher.zoom_user_id or 'me'
        zoom_meetings = self.client.list_meetings(zoom_user_id)

        for zoom_meeting in zoom_meetings.get('meetings', []):
            ZoomMeeting.objects.update_or_create(
                zoom_meeting_id=str(zoom_meeting['id']),
                defaults={
                    'topic': zoom_meeting['topic'],
                    'start_time': datetime.fromisoformat(
                        zoom_meeting['start_time'].replace('Z', '+00:00')
                    ),
                    'duration': zoom_meeting['duration'],
                    'zoom_join_url': zoom_meeting.get('join_url', ''),
                    'status': 'scheduled',
                }
            )

    def get_meeting_recordings(self, meeting):
        """Получение записей встречи"""
        recordings_data = self.client.get_meeting_recordings(meeting.zoom_meeting_id)

        from ..models import ZoomRecording

        for recording in recordings_data.get('recording_files', []):
            ZoomRecording.objects.update_or_create(
                meeting=meeting,
                recording_url=recording['play_url'],
                defaults={
                    'download_url': recording.get('download_url', ''),
                    'duration_seconds': recording.get('duration', 0),
                    'file_size_mb': recording.get('file_size', 0) / (1024 * 1024),
                    'recording_type': recording.get('recording_type', 'shared_screen'),
                }
            )

    def _generate_password(self, length=8):
        """Генерация пароля для встречи"""
        import random
        import string
        return ''.join(random.choices(string.digits, k=length))

    def _sync_recordings(self, meeting):
        """Синхронизация записей после завершения"""
        try:
            self.get_meeting_recordings(meeting)
        except Exception as e:
            logger.error(f"Error syncing recordings: {e}")
