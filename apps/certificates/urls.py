from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('generate/<int:certificate_id>/', views.generate_certificate_pdf, name='generate_pdf'),
    path('verify/<str:qr_code>/', views.verify_certificate, name='verify'),
]
