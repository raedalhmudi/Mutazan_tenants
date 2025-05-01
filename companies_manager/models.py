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

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
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
    # ✅ اسمح بإنشاء ملف شخصي إذا كان المستخدم هو superuser
        if connection.schema_name == 'public' and not self.user.is_superuser:
            return
        super().save(*args, **kwargs)

    
    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} - Profile"
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
    
    
    #-------------essam_edit---------------
    # ██████████████████████████████████████████████
    # ⭐ الإضافات الجديدة المطلوبة للـ Multi-Tenancy
    # ██████████████████████████████████████████████
    
#     # 1. حقل schema_name (مطلوب لـ TenantMixin)
#     auto_create_schema = True  # ينشئ Schema تلقائيًا عند الإنشاء
#     auto_drop_schema = True   # يحذف Schema عند حذف الشركة
    
#     # 2. إعدادات إضافية (اختيارية)
#     class TenantMeta:
#         verbose_name = "الشركة"
#         verbose_name_plural = "الشركات"
    
#     # 3. دالة لحساب اسم الـ Schema (اختياري)
#     def get_schema_name(self):
#         return f"company_{self.id}"  # أو أي تسمية تفضلها

#     def __str__(self):
#         return self.company_name

# class Domain(DomainMixin):
#     pass


#---------------essam_edit_end---------------

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

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            domain_name = f"{self.company_name.lower()}.localhost"
            counter = 1
            while Domain.objects.filter(domain=domain_name).exists():
                domain_name = f"{self.company_name.lower()}{counter}.localhost"
                counter += 1

            try:
                Domain.objects.create(tenant=self, domain=domain_name, is_primary=True)
            except IntegrityError:
                print("❌ خطأ أثناء إنشاء الدومين.")

            # ✅ إنشاء المستخدم الإداري داخل `system_companies`
            if self.admin_user:
                with schema_context(self.schema_name):
                    if not User.objects.filter(username=self.admin_user.username).exists():
                        tenant_admin = User.objects.create_user(
                            username=self.admin_user.username,
                            email=self.admin_user.email,
                            password="Admin@123",
                            is_staff=True,
                            is_superuser=True
                        )
                        tenant_admin.is_staff = True
                        tenant_admin.is_superuser = True
                        tenant_admin.save()

                        

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