from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .permissions import IsDirector
from rest_framework.permissions import IsAuthenticated

User = get_user_model()
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsDirector()]
        return [IsAuthenticated()]
