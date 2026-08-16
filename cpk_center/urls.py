from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from apps.certificates.views import smart_redirect

admin.site.site_header = 'Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi'
admin.site.site_title = 'Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi'
admin.site.index_title = 'Boshqaruv Paneli'

schema_view = get_schema_view(
    openapi.Info(title='CPK Center API', default_version='v1'),
    public=False,
    permission_classes=[permissions.IsAuthenticated],
)

urlpatterns = [
    path('', smart_redirect, name='home'),
    path('zoom/', include('apps.zoom_integration.urls_frontend')),
    path('certificates/', include('apps.certificates.urls')),
    path('groups/', include('apps.groups.urls')),
    path('admin/', admin.site.urls),
    path('kpi/', include('apps.kpi.urls')),
    path('lecturers/', include('apps.lecturers.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('api/', include('apps.certificates.api_urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),

    # Короткие URL личных кабинетов.
    # department_head ведёт через smart_redirect (ранее был 404)
    path('methodist/dashboard/', RedirectView.as_view(url='/certificates/methodist/dashboard/', permanent=False)),
    path('director/dashboard/', RedirectView.as_view(url='/certificates/director/dashboard/', permanent=False)),
    path('department-head/dashboard/', RedirectView.as_view(url='/', permanent=False)),
    path('student/dashboard/', RedirectView.as_view(url='/certificates/student/dashboard/', permanent=False)),

    path('login/', auth_views.LoginView.as_view(template_name='certificates/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
