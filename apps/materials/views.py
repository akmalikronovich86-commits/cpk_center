from rest_framework import viewsets
from .models import Material
from .serializers import MaterialSerializer
from apps.users.permissions import IsDirectorOrLecturer
from rest_framework.permissions import IsAuthenticated

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated(), IsDirectorOrLecturer()]
        return [IsAuthenticated()]
