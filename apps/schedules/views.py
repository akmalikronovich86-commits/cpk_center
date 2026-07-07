from rest_framework import viewsets
from .models import Schedule, Attendance
from .serializers import ScheduleSerializer, AttendanceSerializer
from apps.users.permissions import IsHead, IsDirectorOrHead
from rest_framework.permissions import IsAuthenticated

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsHead()]
        return [IsAuthenticated()]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsDirectorOrHead()]
        return [IsAuthenticated()]
