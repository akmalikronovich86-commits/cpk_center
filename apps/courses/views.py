from rest_framework import viewsets
from .models import Course, Group, Topic, Enrollment
from .serializers import CourseSerializer, GroupSerializer, TopicSerializer, EnrollmentSerializer
from apps.users.permissions import IsDirector, IsDirectorOrMethodist
from rest_framework.permissions import IsAuthenticated

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsDirector()]
        return [IsAuthenticated()]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsDirectorOrMethodist()]
        return [IsAuthenticated()]

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsDirector()]
        return [IsAuthenticated()]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsDirectorOrMethodist()]
        return [IsAuthenticated()]
