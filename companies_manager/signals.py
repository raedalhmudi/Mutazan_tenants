from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.db import connection

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # تحقق من أننا في الـ schema الصحيح
    if connection.schema_name != 'public':
        if created and not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if connection.schema_name != 'public' and hasattr(instance, 'profile'):
        instance.profile.save()