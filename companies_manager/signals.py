from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import Company
from django.db.models.signals import pre_delete
from django.db import connection
# -------------------------------------------
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group  # استبعاد User لتجنب تسجيل التعديلات التلقائية
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import (
    Company, Domain, ViolationsType, ComActivityLog
)
from companies_manager.middleware import get_current_request  # تأكد من وجود هذه الدالة

# -------------------------------------------


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



# signals.py


# قائمة النماذج المستهدفة لتسجيل النشاطات
TARGET_MODELS = [
    Company, Domain, ViolationsType,
    Group  # استبعاد User
]

def log_activity(instance, action, **kwargs):
    if isinstance(instance, ComActivityLog):  # تجنب التسجيلات المتكررة
        return
    # تجاهل الحذف المتسلسل
    if kwargs.get('origin', None) is not None:
        return

    request = get_current_request()
    user = getattr(request, 'user', None) if request else None
    comactivity = getattr(request, 'الشركه', None) if request else None
    ip_address = request.META.get('REMOTE_ADDR') if request else None
    model_verbose_name = instance._meta.verbose_name
    ComActivityLog.objects.create(
        user=user,
        comactivity=comactivity,
        action=f"تم {action} {model_verbose_name} - {str(instance)}",
        module=model_verbose_name,
        ip_address=ip_address,
        extra_data=str(instance)
    )

# تسجيل الإشارات لكل نموذج في القائمة
for model in TARGET_MODELS:
    @receiver(post_save, sender=model)
    def post_save_handler(sender, instance, created, **kwargs):
        action = "إضافة" if created else "تعديل"
        log_activity(instance, action)

    @receiver(post_delete, sender=model)
    def post_delete_handler(sender, instance, **kwargs):
        log_activity(instance, "حذف")

# تسجيل الدخول
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip_address = request.META.get('REMOTE_ADDR')
    ComActivityLog.objects.create(
        user=user,
        action=f" {user.username}-تم تسجيل الدخول للمستخدم ",
        module="المستخدم",
        ip_address=ip_address,
        extra_data=""
    )

# تسجيل الخروج
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ip_address = request.META.get('REMOTE_ADDR')
    ComActivityLog.objects.create(
        user=user,
        action=f"  {user.username}-تم تسجيل الخروج للمستخدم ",
        module="المستخدم",
        ip_address=ip_address,
        extra_data=""
    )
