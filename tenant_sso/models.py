from django.db import models
from django_tenants.models import TenantMixin
from user_management.models import CustomUser

class SSOToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "رمز SSO"
        verbose_name_plural = "رموز SSO"

class TenantSSOConfig(models.Model):
    tenant = models.OneToOneField('companies_manager.Company', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    allowed_domains = models.TextField(help_text="نطاقات مسموح بها (واحد لكل سطر)")
    
    class Meta:
        verbose_name = "إعدادات SSO للمستأجر"
        verbose_name_plural = "إعدادات SSO للمستأجرين"