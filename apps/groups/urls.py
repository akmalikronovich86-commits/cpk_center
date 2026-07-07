from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('statistics/', views.student_statistics, name='student_statistics'),
]
