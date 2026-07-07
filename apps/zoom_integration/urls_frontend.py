from django.urls import path
from . import views_frontend

app_name = 'zoom'

urlpatterns = [
    path('meetings/', views_frontend.meeting_list, name='meeting_list'),
    path('meeting/<int:meeting_id>/', views_frontend.meeting_room, name='meeting_room'),
    path('create-from-schedule/<int:schedule_id>/', views_frontend.create_meeting_from_schedule, name='create_from_schedule'),
    path('webhook/', views_frontend.webhook, name='webhook'),
]
