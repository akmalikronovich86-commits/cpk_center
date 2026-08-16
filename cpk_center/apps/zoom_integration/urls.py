from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'meetings', views.ZoomMeetingViewSet, basename='zoom-meeting')

urlpatterns = [
    path('', include(router.urls)),
]
