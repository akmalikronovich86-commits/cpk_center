# Скрываем стандартные модели auth ДО загрузки админки
import django
from django.apps import apps

def hide_default_auth():
    if apps.ready:
        from django.contrib import admin
        from django.contrib.auth.models import User, Group, Permission
        
        try:
            admin.site.unregister(User)
        except:
            pass
        try:
            admin.site.unregister(Group)
        except:
            pass
        try:
            admin.site.unregister(Permission)
        except:
            pass

# Выполняем после готовности Django
from django.dispatch import receiver
from django.core.signals import setting_changed

# hide_default_auth()  # Будет вызвано в apps.py
