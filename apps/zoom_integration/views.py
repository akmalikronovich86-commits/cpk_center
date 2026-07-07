from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ZoomMeeting, ZoomRecording
from .serializers import ZoomMeetingSerializer, ZoomRecordingSerializer
from .services import MeetingService


class ZoomMeetingViewSet(viewsets.ModelViewSet):
    """API для управления Zoom-встречами"""
    serializer_class = ZoomMeetingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            return ZoomMeeting.objects.filter(teacher=user)
        elif user.is_student:
            return ZoomMeeting.objects.filter(
                schedule__group__students=user
            )
        return ZoomMeeting.objects.all()
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Начать встречу"""
        meeting = self.get_object()
        service = MeetingService(meeting.zoom_account)
        service.start_meeting(meeting)
        return Response({'status': 'started', 'join_url': meeting.zoom_join_url})
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """Завершить встречу"""
        meeting = self.get_object()
        service = MeetingService(meeting.zoom_account)
        service.end_meeting(meeting)
        return Response({'status': 'ended'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отменить встречу"""
        meeting = self.get_object()
        service = MeetingService(meeting.zoom_account)
        service.cancel_meeting(meeting)
        return Response({'status': 'cancelled'})
    
    @action(detail=True, methods=['get'])
    def recordings(self, request, pk=None):
        """Получить записи встречи"""
        meeting = self.get_object()
        recordings = ZoomRecording.objects.filter(meeting=meeting)
        serializer = ZoomRecordingSerializer(recordings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Предстоящие встречи"""
        queryset = self.get_queryset().filter(
            status='scheduled',
            start_time__gte=timezone.now()
        ).order_by('start_time')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def live(self, request):
        """Текущие встречи"""
        queryset = self.get_queryset().filter(status='live')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
