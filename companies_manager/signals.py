from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import Company
from django.db.models.signals import pre_delete
from django.db import connection


@receiver(post_save, sender=User)
def encrypt_password_on_create(sender, instance, created, **kwargs):
    if created:
        raw_password = instance.password
        # ✅ نتأكد إن كلمة السر مش مشفرة
        if not raw_password.startswith('pbkdf2_sha256$'):
            instance.password = make_password(raw_password)
            # نستخدم transaction.on_commit عشان ما يصير save داخل save
            transaction.on_commit(lambda: instance.save())




@receiver(pre_delete, sender=Company)
def delete_company_schema(sender, instance, **kwargs):
    schema_name = instance.schema_name
    if schema_name == "public":
        raise ValueError("⚠️ لا يمكن حذف الأسكيما الافتراضية!")

    # حذف الدومينات المرتبطة
    instance.domains.all().delete()

    # حذف الأسكيما الخاصة بالشركة
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
            print(f"✅ تم حذف الأسكيما {schema_name} بنجاح.")
    except Exception as e:
        print(f"❌ خطأ أثناء حذف الأسكيما {schema_name}: {e}")
