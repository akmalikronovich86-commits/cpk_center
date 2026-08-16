from django.urls import path

from . import views

app_name = 'kpi'

urlpatterns = [
    path('dashboard/', views.department_head_kpi_dashboard, name='department_head_kpi_dashboard'),
    path('attestation-report/', views.attestation_kpi_report, name='attestation_kpi_report'),
    path('export/excel/', views.export_kpi_report_excel, name='export_kpi_excel'),
    path('ijro-tasks/', views.ijro_tasks_list, name='ijro_tasks_list'),
    path('ijro-tasks/create/', views.ijro_task_create, name='ijro_task_create'),
    path('ijro-tasks/<int:task_id>/update/', views.ijro_task_update, name='ijro_task_update'),
    path('ijro-tasks/<int:task_id>/delete/', views.ijro_task_delete, name='ijro_task_delete'),

    # === УПРАВЛЕНИЕ (Bo'lim boshlig'i) ===
    # Расписание (Dars jadvali)
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('schedules/<int:schedule_id>/update/', views.schedule_update, name='schedule_update'),
    path('schedules/<int:schedule_id>/delete/', views.schedule_delete, name='schedule_delete'),

    # Курсы (Kurslar)
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/update/', views.course_update, name='course_update'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),

    # Группы (Guruhlar)
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/update/', views.group_update, name='group_update'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),

    # Студенты (Tinglovchilar)
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:student_id>/update/', views.student_update, name='student_update'),
    path('students/<int:student_id>/delete/', views.student_delete, name='student_delete'),


    # Преподаватели (Ma'ruzachilar)
    path('lecturers/', views.lecturer_list, name='lecturer_list'),
    path('lecturers/create/', views.lecturer_create, name='lecturer_create'),
    path('lecturers/<int:lecturer_id>/update/', views.lecturer_update, name='lecturer_update'),
    path('lecturers/<int:lecturer_id>/delete/', views.lecturer_delete, name='lecturer_delete'),
]
