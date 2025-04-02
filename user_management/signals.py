# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django_tenants.utils import tenant_context
# from user_management.models import CustomUser
# from companies_manager.models import Company

# @receiver(post_save, sender=CustomUser)
# def sync_user_to_tenants(sender, instance, created, **kwargs):
#     """
#     مزامنة المستخدم مع جميع الشركات التي يديرها
#     """
#     if instance.managed_company:
#         with tenant_context(instance.managed_company):
#             # إنشاء/تحديث المستخدم في مخطط المستأجر
#             User = sender  # نفس نموذج المستخدم
#             user_data = {
#                 'username': instance.username,
#                 'email': instance.email,
#                 'first_name': instance.first_name,
#                 'last_name': instance.last_name,
#                 'phone_number': instance.phone_number,
#                 'national_id': instance.national_id,
#                 'is_staff': True,
#                 'is_superuser': True,
#             }
            
#             if created:
#                 User.objects.create(**user_data)
#             else:
#                 User.objects.filter(username=instance.username).update(**user_data)

# @receiver(post_save, sender=Company)
# def create_tenant_admin(sender, instance, created, **kwargs):
#     """
#     إنشاء مستخدم إداري عند إنشاء شركة جديدة
#     """
#     if created and instance.admin_user:
#         with tenant_context(instance):
#             User = CustomUser
#             if not User.objects.filter(username=instance.admin_user.username).exists():
#                 User.objects.create_superuser(
#                     username=instance.admin_user.username,
#                     email=instance.admin_user.email,
#                     password="Admin@123",
#                     phone_number=instance.admin_user.phone_number,
#                     national_id=instance.admin_user.national_id,
#                     is_staff=True,
#                     is_superuser=True
#                 )