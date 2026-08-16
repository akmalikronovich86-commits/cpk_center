from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User

from .models import StudentRecord


@receiver(post_save, sender=User)
def create_student_record(sender, instance, created, **kwargs):
    """Автоматическое создание StudentRecord при создании User с role='student'"""
    if created and instance.role == 'student':
        if instance.phone:
            # Передаём пустую строку вместо None для passport
            StudentRecord.objects.get_or_create(
                user=instance,
                defaults={
                    'full_name': instance.full_name or '',
                    'phone': instance.phone or '',
                    'position': instance.position or '',
                    'passport': '',  # Пустая строка вместо None
                    'xtm': '',
                    'birth_date': '',
                    'group': '',
                    'branch': '',
                    'district_power': '',
                    'grade': '',
                    'topic': '',
                    'period': '',
                }
            )


@receiver(post_save, sender=User)
def update_student_record(sender, instance, **kwargs):
    """Синхронизация данных User с StudentRecord"""
    if instance.role == 'student' and hasattr(instance, 'student_record'):
        record = instance.student_record
        changed = False

        if instance.full_name and record.full_name != instance.full_name:
            record.full_name = instance.full_name
            changed = True

        if instance.phone and record.phone != instance.phone:
            record.phone = instance.phone
            changed = True

        if instance.position and record.position != instance.position:
            record.position = instance.position
            changed = True

        if changed:
            record.save()



@receiver(post_save, sender=StudentRecord)
def student_record_created(sender, instance, created, **kwargs):
    """Автоматическое создание User с паролем при создании StudentRecord"""
    if created and not instance.user:
        import secrets

        from django.db.models.signals import post_save as ps_signal
        from django.utils.crypto import get_random_string

        import apps.groups.signals as signals_module
        from apps.users.models import User

        # Генерируем username из паспорта
        if instance.passport:
            username = f"Tinglovchi_{instance.passport.replace(' ', '')}"
        else:
            username = f"Student_{secrets.token_hex(4)}"

        # Проверяем уникальность
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1

        # Генерируем случайный пароль
        password = get_random_string(length=10)

        # Временно отключаем сигнал create_student_record, чтобы избежать дублирования
        ps_signal.disconnect(signals_module.create_student_record, sender=User)
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=instance.email or '',  # Используем email из StudentRecord
                role='student',
                full_name=instance.full_name or '',
                phone=instance.phone or '',
                position=instance.position or '',
            )
            # Привязываем пользователя к студенту
            instance.user = user
            instance.save(update_fields=['user'])
        finally:
            # Включаем сигнал обратно
            ps_signal.connect(signals_module.create_student_record, sender=User)

        print(f"✅ Пользователь создан: {username}, пароль: {password}")
        # Отправляем email с логином и паролем
        if instance.email:
            try:
                from apps.certificates.utils import send_credentials_email
                send_credentials_email(user, password)
            except Exception as e:
                print(f"️ Ошибка при отправке email: {e}")
        else:
            print("⚠️ Email не указан. Администратор может добавить email вручную.")
