from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import MaterialViewSet
router = SimpleRouter()
router.register(r'materials', MaterialViewSet)
urlpatterns = [path('', include(router.urls))]
