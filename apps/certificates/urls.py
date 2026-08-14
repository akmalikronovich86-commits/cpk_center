from django.urls import path
from . import views, views_department_head

app_name = 'certificates'

urlpatterns = [
    path('generate/<int:certificate_id>/', views.generate_certificate_pdf, name='generate_pdf'),
    path('verify/<str:qr_code>/', views.verify_certificate, name='verify'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/results/', views.student_results, name='student_results'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),
    path('student/announcements/', views.student_announcements, name='student_announcements'),
    path('student/materials/', views.student_materials, name='student_materials'),
    path('student/zoom/', views.student_zoom_recordings, name='student_zoom_recordings'),
    path('student/change-password/', views.change_password, name='change_password'),

    path('director/dashboard/', views.director_dashboard, name='director_dashboard'),
    path('methodist/dashboard/', views.methodist_dashboard, name='methodist_dashboard'),
    path('lecturer/dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),

    # Department Head - Управление расписанием
    path('department-head/schedule/create/', views_department_head.schedule_create, name='schedule_create'),
    path('department-head/schedule/<int:schedule_id>/edit/', views_department_head.schedule_edit, name='schedule_edit'),
    path('department-head/schedule/<int:schedule_id>/delete/', views_department_head.schedule_delete, name='schedule_delete'),
    
    # Department Head - Управление группами
    path('department-head/group/create/', views_department_head.group_create, name='group_create'),
    path('department-head/group/<int:group_id>/edit/', views_department_head.group_edit, name='group_edit'),
    path('department-head/group/<int:group_id>/delete/', views_department_head.group_delete, name='group_delete'),
    
    # Department Head - Назначение лекторов
    path('department-head/assign-lecturer/', views_department_head.assign_lecturer, name='assign_lecturer'),
]
