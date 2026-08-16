from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import AttendanceViewSet, ScheduleViewSet

router = SimpleRouter()
router.register(r'schedules', ScheduleViewSet)
router.register(r'attendances', AttendanceViewSet)
urlpatterns = [path('', include(router.urls))]
