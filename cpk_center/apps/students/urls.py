from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import StudentViewSet

router = SimpleRouter()
router.register(r'students', StudentViewSet)
urlpatterns = [path('', include(router.urls))]
