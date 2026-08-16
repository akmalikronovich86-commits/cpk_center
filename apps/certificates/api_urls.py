from django.urls import path

from . import api_views

app_name = 'api'

urlpatterns = [
    path('certificates/verify/<str:qr_code>/', api_views.verify_certificate_api, name='verify'),
]
