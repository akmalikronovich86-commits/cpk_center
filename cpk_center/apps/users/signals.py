from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LecturerProfile, StudentProfile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'lecturer':
            LecturerProfile.objects.create(user=instance, specialization='Noma\'lum')
