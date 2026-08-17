from django.urls import path
from . import excel_views

app_name = 'reports'

urlpatterns = [
    path('', excel_views.reports_index, name='index'),
    path('students/', excel_views.export_students, name='students_excel'),
    path('certificates/', excel_views.export_certificates, name='certificates_excel'),
    path('schedule/', excel_views.export_schedule, name='schedule_excel'),
    path('lecturers/', excel_views.export_lecturers, name='lecturers_excel'),
]
