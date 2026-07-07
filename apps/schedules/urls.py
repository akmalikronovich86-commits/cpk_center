from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ScheduleViewSet, AttendanceViewSet
router = SimpleRouter()
router.register(r'schedules', ScheduleViewSet)
router.register(r'attendances', AttendanceViewSet)
urlpatterns = [path('', include(router.urls))]
