from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = "Autentifikatsiya va Avtorizatsiya"

    def ready(self):
        # Этот метод вызывается ПОСЛЕ загрузки всех приложений в INSTALLED_APPS
        from django.contrib import admin
        from django.contrib.auth.models import User as DjangoUser, Group, Permission
        
        # Скрываем стандартные модели auth
        for model in (DjangoUser, Group, Permission):
            try:
                admin.site.unregister(model)
            except admin.sites.NotRegistered:
                pass
