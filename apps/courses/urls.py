from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CourseViewSet, GroupViewSet, TopicViewSet, EnrollmentViewSet
router = SimpleRouter()
router.register(r'courses', CourseViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'enrollments', EnrollmentViewSet)
urlpatterns = [path('', include(router.urls))]
