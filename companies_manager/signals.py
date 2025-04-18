from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction

@receiver(post_save, sender=User)
def encrypt_password_on_create(sender, instance, created, **kwargs):
    if created:
        raw_password = instance.password
        # ✅ نتأكد إن كلمة السر مش مشفرة
        if not raw_password.startswith('pbkdf2_sha256$'):
            instance.password = make_password(raw_password)
            # نستخدم transaction.on_commit عشان ما يصير save داخل save
            transaction.on_commit(lambda: instance.save())
