from rest_framework import viewsets
from apps.users.models import User
from apps.users.serializers import UserSerializer
from apps.users.permissions import IsDirectorOrMethodist
from rest_framework.permissions import IsAuthenticated

class StudentViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='student')
    serializer_class = UserSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsDirectorOrMethodist()]
        return [IsAuthenticated()]
