from django.urls import path

from . import views

app_name = 'assessments'

urlpatterns = [
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('department/report/', views.department_report, name='department_report'),
    path('director/dashboard/', views.director_dashboard, name='director_dashboard'),
]
