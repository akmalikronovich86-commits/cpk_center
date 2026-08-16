from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CourseViewSet, EnrollmentViewSet, GroupViewSet, TopicViewSet

router = SimpleRouter()
router.register(r'courses', CourseViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'enrollments', EnrollmentViewSet)
urlpatterns = [path('', include(router.urls))]
