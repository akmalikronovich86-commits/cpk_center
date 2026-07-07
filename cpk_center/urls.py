from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Настройка заголовков админ-панели
admin.site.site_header = "Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi"
admin.site.site_title = "Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi"
admin.site.index_title = "Boshqaruv Paneli"
urlpatterns = [
    path('zoom/', include('apps.zoom_integration.urls_frontend')),
    path('certificates/', include('apps.certificates.urls')),
    path('groups/', include('apps.groups.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
