from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ExamQuestionViewSet, ExamResultViewSet, TestSessionViewSet

router = SimpleRouter()
router.register(r'exam-questions', ExamQuestionViewSet)
router.register(r'exam-results', ExamResultViewSet)
router.register(r'test-sessions', TestSessionViewSet)
urlpatterns = [path('', include(router.urls))]
