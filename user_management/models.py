from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    # الحقول الإضافية المشتركة بين جميع المستأجرين
    phone_number = models.CharField(
        max_length=15,
        verbose_name="رقم الهاتف",
        validators=[RegexValidator(r'^\d+$', message="يجب أن يحتوي على أرقام فقط")]
    )
    national_id = models.CharField(
        max_length=20,
        verbose_name="رقم الهوية",
        unique=True,
        null=True,
        blank=True
    )
    profile_picture = models.ImageField(
        upload_to="user_profiles/%Y/%m/%d",
        verbose_name="صورة الملف الشخصي",
        null=True,
        blank=True
    )
    
    # علاقة مع الشركة (للمستخدمين الإداريين)
    managed_company = models.OneToOneField(
        'companies_manager.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manager_profile',
        verbose_name="الشركة المدارة"
    )
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"