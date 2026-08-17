from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('qr/<int:schedule_id>/', views.generate_qr, name='generate_qr'),
    path('scan/', views.scan_attendance, name='scan'),
]
