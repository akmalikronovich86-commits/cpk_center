from django.urls import path

from .views import (
    AttendanceReportView,
    ExamResultsReportView,
    LecturerLoadReportView,
    ScheduleReportView,
    StudentListReportView,
)

urlpatterns = [
    path('reports/lecturer-load/', LecturerLoadReportView.as_view()),
    path('reports/attendance/', AttendanceReportView.as_view()),
    path('reports/schedule/', ScheduleReportView.as_view()),
    path('reports/students/', StudentListReportView.as_view()),
    path('reports/exam-results/', ExamResultsReportView.as_view()),
]
