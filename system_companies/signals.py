# # system_companies/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# from django_tenants.utils import schema_context
# from .models import TenantAwareUser

# User = get_user_model()

# @receiver(post_save, sender=User)
# def create_tenant_aware_user(sender, instance, created, **kwargs):
#     if created:
#         # البحث عن الشركة المرتبطة بهذا المستخدم
#         from companies_manager.models import Company
#         company = Company.objects.filter(admin_user=instance).first()
        
#         if company:
#             # إنشاء TenantAwareUser في الإسكيما العامة
#             TenantAwareUser.objects.get_or_create(
#                 user=instance,
#                 tenant=company
#             )
            
#             # إنشاء نسخة من المستخدم في إسكيما الشركة
#             with schema_context(company.schema_name):
#                 if not User.objects.filter(username=instance.username).exists():
#                     User.objects.create(
#                         username=instance.username,
#                         email=instance.email,
#                         is_staff=True,
#                         is_superuser=True,
#                         is_active=True
#                     )