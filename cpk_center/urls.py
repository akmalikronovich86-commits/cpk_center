from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

from apps.certificates.views import smart_redirect

# Настройка заголовков админ-панели
admin.site.site_header = "Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi"
admin.site.site_title = "Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi"
admin.site.index_title = "Boshqaruv Paneli"

urlpatterns = [
    path('', smart_redirect, name='home'),
    path('zoom/', include('apps.zoom_integration.urls_frontend')),
    path('certificates/', include('apps.certificates.urls')),
    path('groups/', include('apps.groups.urls')),
    path('admin/', admin.site.urls),
    path('kpi/', include('apps.kpi.urls')),
    path('lecturers/', include('apps.lecturers.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('reports/', include('apps.reports.urls')),

    # Короткие URL для личных кабинетов (перенаправления)
    path('methodist/dashboard/', RedirectView.as_view(url='/certificates/methodist/dashboard/', permanent=False), name='methodist_dashboard_short'),
    path('director/dashboard/', RedirectView.as_view(url='/certificates/director/dashboard/', permanent=False), name='director_dashboard_short'),
    path('department-head/dashboard/', RedirectView.as_view(url='/kpi/dashboard/', permanent=False), name='department_head_dashboard_short'),
    path('student/dashboard/', RedirectView.as_view(url='/certificates/student/dashboard/', permanent=False), name='student_dashboard_short'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='certificates/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
