from rest_framework import serializers

from .models import Attendance, Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta: model = Schedule; fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta: model = Attendance; fields = '__all__'
