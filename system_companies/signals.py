# signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import connection
from django.contrib.auth.models import Group  # استبعاد User لتجنب تسجيل التعديلات التلقائية
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import (
    DriverNeme, Trucks, Material, Legal_weight, WeightCard,WeightCardMaterial,
    Invoice, Devices, Entry_and_exit, ViolationRecord, Attendance,
    ActivityLog
)

from system_companies.middleware import get_current_request  # تأكد من وجود هذه الدالة

# قائمة النماذج المستهدفة لتسجيل النشاطات
TARGET_MODELS = [
    DriverNeme, Trucks, Material, Legal_weight, WeightCard,
    Invoice, Devices, Entry_and_exit, ViolationRecord, Attendance,
    Group  # استبعاد User
]

def log_activity(instance, action, **kwargs):
    # تجاهل الحذف المتسلسل
    if kwargs.get('origin', None) is not None:
        return

    request = get_current_request()
    user = getattr(request, 'user', None) if request else None
    ip_address = request.META.get('REMOTE_ADDR') if request else None
    model_verbose_name = instance._meta.verbose_name
    ActivityLog.objects.create(
        user=user,
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


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if connection.schema_name == 'public':
        return  # لا تسجل النشاط إذا كنا في public schema

    ip_address = request.META.get('REMOTE_ADDR')
    ActivityLog.objects.create(
        user=user,
        action=f"تم تسجيل الخروج للمستخدم - {user.username}",
        module="المستخدم",
        ip_address=ip_address,
        extra_data=""
    )


# تسجيل الخروج
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if connection.schema_name == 'public':
        return
    ip_address = request.META.get('REMOTE_ADDR')
    ActivityLog.objects.create(
        user=user,
        action=f"تم تسجيل الخروج للمستخدم - {user.username}",
        module="المستخدم",
        ip_address=ip_address,
        extra_data=""
    )
# -----------------------------خصم الكميه من الماده--------------------

# استرجاع الكمية عند الحذف
@receiver(post_delete, sender=WeightCardMaterial)
def return_material_quantity(sender, instance, **kwargs):
    material = instance.material
    material.quantity_mat += instance.quantity
    material.save()
