from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import connection, transaction, IntegrityError
from django_tenants.utils import schema_context
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.postgres.fields import ArrayField 
from django.dispatch import receiver
import re
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='public_profile',  # ✅ غيرنا هنا
        verbose_name="المستخدم"
    )

    phone_number = models.CharField(
        max_length=15,
        verbose_name="رقم الهاتف",
        validators=[RegexValidator(r'^\d+$', message="يجب أن يحتوي على أرقام فقط")],
        blank=True,
        null=True
    )
    address = models.TextField(verbose_name="عنوان السكن", blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="user_profiles/%Y/%m/%d",
        verbose_name="صورة المستخدم",
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        # السماح بإنشاء ملف شخصي لجميع المستخدمين في الأسكيما العامة
        if connection.schema_name == 'public':
            super().save(*args, **kwargs)
        # للمستخدمين في الشركات (Tenants) فقط إذا كانوا superuser
        elif self.user.is_superuser:
            super().save(*args, **kwargs)

        
    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"
        db_table = 'companies_manager_userprofile'

# إزالة الإشارات (signals) السابقة واستبدالها بهذه
@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    if connection.schema_name != 'public':
        return
    
    if created:
        # التحقق من عدم وجود ملف شخصي بالفعل
        if not hasattr(instance, 'public_profile'):
            UserProfile.objects.create(user=instance)
    else:
        # تحديث الملف الشخصي إذا كان موجوداً
        if hasattr(instance, 'public_profile'):
            instance.public_profile.save()
# ===================================C:\Users\lenovo\Desktop\Mutazan\companies_manager\management=


User = get_user_model()
 # 🔥 جلب نموذج المستخدم الصحيح

class Company(TenantMixin):
    company_name = models.CharField(
        max_length=100,
        verbose_name="اسم الشركة",
        validators=[RegexValidator(r'^[\D]+$', message="يجب ألا يحتوي على أرقام")]
    )
    business_type = models.CharField(max_length=255, verbose_name="نوع النشاط")
    registration_number = models.PositiveIntegerField(unique=True, verbose_name="رقم السجل التجاري")
    country = models.CharField(
        max_length=100, 
        verbose_name="الدولة",
        validators=[RegexValidator(r'^[\D]+$', message="يجب ألا يحتوي على أرقام")]
    )
    address = models.CharField(max_length=255, verbose_name="العنوان")
    phone_number = models.CharField(
        max_length=15,
        verbose_name="رقم الهاتف",
        validators=[RegexValidator(r'^\d+$', message="يجب أن يحتوي على أرقام فقط")]
    )
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    logo = models.ImageField(upload_to="company_logos/%Y/%m/%d", verbose_name="شعار الشركة")
    employees_count = models.PositiveIntegerField(verbose_name="عدد الموظفين")
    founded_date = models.DateField(verbose_name="تاريخ التأسيس")
    services_offered = models.TextField(verbose_name="الخدمات المقدمة")
    port_license_number = models.PositiveIntegerField(unique=True, verbose_name="تصريح العمل بالميناء")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    # 🔥 المسؤول الإداري المرتبط بالشركة (يجب أن يكون موجودًا مسبقًا في النظام الرئيسي)
    admin_user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="المسؤول الإداري"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "الشركات"

    def clean(self):
        super().clean()

        if self.admin_user and not hasattr(self.admin_user, 'public_profile'):
            raise ValidationError({"admin_user": "⚠️ المستخدم المختار لا يملك ملفًا شخصيًا. الرجاء إنشاء ملف شخصي أولاً."})

        # توليد اسم الأسكيما من اسم الشركة
        self.schema_name = self.company_name.lower().replace(" ", "_")

        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.schema_name):
            raise ValidationError("اسم الأسكيما غير صالح. يجب أن يحتوي على أحرف وأرقام فقط، ويبدأ بحرف.")

        if Company.objects.exclude(pk=self.pk).filter(schema_name=self.schema_name).exists():
            raise ValidationError(f"اسم الأسكيما '{self.schema_name}' موجود بالفعل. يرجى اختيار اسم آخر.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_admin_user = None

        if not is_new and self.pk:
            old_admin_user = Company.objects.get(pk=self.pk).admin_user

        self.schema_name = self.company_name.lower().replace(" ", "_")
        self.full_clean()
        super().save(*args, **kwargs)

        if is_new:
            # كود إنشاء السكيمه والدومين والمستخدم الإداري الجديد (نفس الكود اللي كتبته انت)
            domain_name = f"{self.company_name.lower().replace(' ', '')}.localhost"
            counter = 1
            while Domain.objects.filter(domain=domain_name).exists():
                domain_name = f"{self.company_name.lower().replace(' ', '')}{counter}.localhost"
                counter += 1

            try:
                Domain.objects.create(tenant=self, domain=domain_name, is_primary=True)
            except IntegrityError:
                print("❌ خطأ أثناء إنشاء الدومين.")

            if self.admin_user:
                with schema_context(self.schema_name):
                    # 🔥 تحقق هل المستخدم موجود داخل سكيمه الشركة
                    tenant_user = User.objects.filter(username=self.admin_user.username).first()
                    if not tenant_user:
                        # 🔥 المستخدم غير موجود، أنشئه
                        tenant_user = User.objects.create_user(
                            username=self.admin_user.username,
                            email=self.admin_user.email,
                            password="Admin@123",
                            is_staff=True,
                            is_superuser=True
                        )
                        tenant_user.save()

                    # 🔥 بعدها تأكد من إنشاء ملف شخصي له داخل السكيمه الخاصة
                    from system_companies.models import UserProfile as TenantUserProfile

                    if not TenantUserProfile.objects.filter(user=tenant_user).exists():
                        TenantUserProfile.objects.create(
                            user=tenant_user,
                            phone_number=getattr(self.admin_user.public_profile, 'phone_number', ''),
                            address=getattr(self.admin_user.public_profile, 'address', ''),
                            profile_picture=getattr(self.admin_user.public_profile, 'profile_picture', None)
                        )

        else:
            # ✨✨ هنا نتأكد اذا الادمن تغير ✨✨
            if old_admin_user != self.admin_user:
                if self.admin_user:
                    with schema_context(self.schema_name):
                        # 🔥 حذف المدير القديم مع ملفه الشخصي إن وجد
                        if old_admin_user:
                            try:
                                old_tenant_user = User.objects.get(username=old_admin_user.username)
                                # حذف UserProfile الخاص به أولاً
                                if hasattr(old_tenant_user, 'public_profile'):
                                    old_tenant_user.public_profile.delete()
                                old_tenant_user.delete()
                                print(f"✅ تم حذف المدير القديم: {old_admin_user.username}")
                            except User.DoesNotExist:
                                print(f"⚠️ المدير القديم {old_admin_user.username} غير موجود داخل السكيمة.")
                        
                        # 🔥 إنشاء المدير الجديد
                        if not User.objects.filter(username=self.admin_user.username).exists():
                            tenant_admin = User.objects.create_user(
                                username=self.admin_user.username,
                                email=self.admin_user.email,
                                password="Admin@123",
                                is_staff=True,
                                is_superuser=True
                            )
                            tenant_admin.save()

                            from system_companies.models import UserProfile as TenantUserProfile

                            TenantUserProfile.objects.create(
                                user=tenant_admin,
                                phone_number=getattr(self.admin_user.public_profile, 'phone_number', ''),
                                address=getattr(self.admin_user.public_profile, 'address', ''),
                                profile_picture=getattr(self.admin_user.public_profile, 'profile_picture', None)
                            )






                        

    def delete(self, *args, **kwargs):
        """ حذف الشركة مع قاعدة بياناتها """
        schema_name = self.schema_name
        if schema_name == "public":
            raise ValueError("⚠️ لا يمكن حذف الأسكيما الافتراضية!")

        self.domains.all().delete()

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
        except Exception as e:
            print(f"❌ خطأ أثناء حذف الأسكيما {schema_name}: {e}")

        super().delete(*args, **kwargs)

class Domain(DomainMixin):
    tenant = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="domains")
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.domain

# -----------------------------------------------------------
#  ------------------------نوع المخالفات----------------------------


class ViolationsType(models.Model):
    NAME_VIOLATION = [
        ('Reverse entry path', 'عكس مسار دخول'),
        ('Reverse exit path', 'عكس مسار خروج'),
        ('Entry without a plate', 'دخول بغير لوحه '),
        ('Exit without a plate', 'خروج بغير لوحه '),
        ('No first weight card', 'عدم وجود بطاقة وزن اولى'),
        ('Exceeding the legal weight', 'تجاوز الوزن القانوني '),
        ('Incomplete data', 'بيانات غير مكتمله'),
        ('Incorrect invoice', 'فاتوره غير صحيحه'),
    ]

    name = models.CharField(max_length=255,choices=NAME_VIOLATION,verbose_name="اسم المخالفة")  # مثل "تجاوز الوزن القانوني"
    description = models.TextField(verbose_name="وصف المخالفة", null=True, blank=True)  # تفاصيل إضافية عن المخالفة
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قيمة الغرامة")  # قيمة الغرامة المالية
    violation_code = models.CharField(max_length=50, unique=True, verbose_name="رمز المخالفة")  # رمز فريد لكل مخالفة
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")  # متى أُضيفت المخالفة
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")  # متى تم تعديلها آخر مرة

    class Meta:
        verbose_name = "نوع المخالفة"
        verbose_name_plural = "أنواع المخالفات"

    def __str__(self):
        return self.name

# -----------------------------------------------------------
#  ---------------------------------------------------

# في تطبيق companies_manager

class WeightCardMain(models.Model):
    schema_name = models.CharField(max_length=50, verbose_name="اسم الـ Schema")  # ربط البطاقة بالشركة
    plate_number = models.CharField(max_length=50, verbose_name="رقم اللوحة ")
    violation_type = models.CharField(max_length=255, verbose_name=" نوع المخالفة ", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ ووقت المخالفة ")
    device_vio = models.CharField(max_length=255, verbose_name=" الكاميرا ", null=True, blank=True)
    entry_exit_log = models.CharField(max_length=255, verbose_name="العمليه ", null=True, blank=True)
    weight_card_vio = models.CharField(max_length=255, verbose_name="بطاقة الوزن", null=True, blank=True)
    empty_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الفارغ", null=True, blank=True)
    loaded_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن المحمل", null=True, blank=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الصافي", null=True, blank=True)
    driver_name = models.CharField(max_length=255, verbose_name="اسم السائق", null=True, blank=True)
    entry_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الدخول")
    exit_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الخروج")
    quantity = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الكمية", null=True, blank=True)
    material = models.CharField(max_length=255, verbose_name="المادة", null=True, blank=True)
    status = models.CharField(max_length=10, choices=[
        ('incomplete', 'بطاقة غير مكتملة ❌'),
        ('complete', 'بطاقة مكتملة ✅'),
    ], default='incomplete', verbose_name="حالة البطاقة")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "بطاقة الوزن الرئيسية"
        verbose_name_plural = "بطاقات الوزن الرئيسية"

    def __str__(self):
        return f"{self.plate_number} - {self.schema_name}"


# -----------------------------------------------------------
#  ---------------------------------------------------


# class ViolationRecord(models.Model):
#     schema_name = models.CharField(max_length=50, verbose_name="اسم الـ Schema")
#     plate_number_vio = models.CharField(max_length=255, verbose_name="رقم اللوحه", null=True, blank=True)
#     violation_type = models.CharField("companies_manager.ViolationsType", on_delete=models.CASCADE, verbose_name=" نوع المخالفة")
#     timestamp = models.DateTimeField(auto_now_add=True)
#     device_vio = models.CharField(max_length=255, verbose_name="الكاميرا", null=True, blank=True)
#     entry_exit_log = models.CharField(max_length=255, verbose_name="العمليه", null=True, blank=True)
#     weight_card_vio = models.CharField(max_length=255, verbose_name="بطاقة الوزن", null=True, blank=True)
#     image_violation = models.ImageField(upload_to="images_violation/%y/%m/%d", verbose_name="صور المخالفة")

#     class Meta:
#         verbose_name = " المخالفه"
#         verbose_name_plural = "المخالفات"

#     def __str__(self):
#         return self.plate_number_vio


















