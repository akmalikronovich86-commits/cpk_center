from rest_framework import serializers

from .models import Course, Enrollment, Group, Topic


class CourseSerializer(serializers.ModelSerializer):
    class Meta: model = Course; fields = '__all__'
class GroupSerializer(serializers.ModelSerializer):
    class Meta: model = Group; fields = '__all__'
class TopicSerializer(serializers.ModelSerializer):
    class Meta: model = Topic; fields = '__all__'
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta: model = Enrollment; fields = '__all__'
