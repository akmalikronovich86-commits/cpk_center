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
