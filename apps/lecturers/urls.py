from django.urls import path
from django.views.generic import RedirectView

from . import views, views_crud

app_name = 'lecturers'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='lecturers:lecturer_dashboard'), name='index'),
    # Dashboard и основные страницы (только просмотр)
    path('dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('schedule/', views.lecturer_schedule, name='lecturer_schedule'),
    path('courses/', views.lecturer_courses, name='lecturer_courses'),
    path('students/', views.lecturer_students, name='lecturer_students'),
    path('materials/', views.lecturer_materials, name='lecturer_materials'),
    path('zoom/', views.lecturer_zoom, name='lecturer_zoom'),

    # Material CRUD (загрузка, редактирование, удаление)
    path('materials/upload/', views.upload_material, name='upload_material'),
    path('materials/<int:material_id>/edit/', views_crud.material_edit, name='material_edit'),
    path('materials/<int:material_id>/delete/', views_crud.material_delete, name='material_delete'),

    # Schedule (редактирование и удаление, но не создание)
    path('schedule/<int:schedule_id>/edit/', views_crud.schedule_edit, name='schedule_edit'),
    path('schedule/<int:schedule_id>/delete/', views_crud.schedule_delete, name='schedule_delete'),

    # Attendance (просмотр и отметка)
    path('attendance/', views.lecturer_attendance, name='lecturer_attendance'),
    path('attendance/<int:schedule_id>/', views.lecturer_attendance_detail, name='lecturer_attendance_detail'),
    path('attendance/<int:schedule_id>/mark/', views.mark_attendance, name='mark_attendance'),

    # Exam results (ввод результатов экзамена)
    path('exam-results/', views.lecturer_exam_results, name='lecturer_exam_results'),
    path('exam-results/group/<int:group_id>/', views.lecturer_exam_results_group, name='lecturer_exam_results_group'),
    path('exam-results/group/<int:group_id>/save/', views.save_exam_results, name='save_exam_results'),
]
