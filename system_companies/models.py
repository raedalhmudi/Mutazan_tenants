from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth import get_user_model  # استخدم هذا بدلاً من User مباشرة
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import now
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField  # if using PostgreSQL
from django.conf import settings
from django.db import connection
import cv2
from companies_manager.models import ViolationsType , Legal_weight

import socket
import serial.tools.list_ports
import serial
from django.core.validators import RegexValidator

from django.contrib.auth import get_user_model


User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='company_profile',  # ✅ وهنا كمان غيرنا
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

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"
        db_table = 'system_companies_userprofile'  # تأكد أن تغير اسم الجدول ليكون خاص بالشركة

# إزالة الإشارات (signals) السابقة واستبدالها بهذه
@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    if connection.schema_name != 'tenants':
        return
    
    if created:
        # التحقق من عدم وجود ملف شخصي بالفعل
        if not hasattr(instance, 'company_profile'):
            UserProfile.objects.create(user=instance)
    else:
        # تحديث الملف الشخصي إذا كان موجوداً
        if hasattr(instance, 'company_profile'):
            instance.company_profile.save()

# -----------------------------------------------------------
#  -----------------------  سجل النشاطات----------------------------

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    module = models.CharField(max_length=200, blank=True, help_text="اسم القسم الذي حدث فيه الإجراء (مثل الشاحنات، الوزن)")
    extra_data = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "سجل النشاط "
        verbose_name_plural = "سجل النشاطات"
        # هذا مهم جداً!
        app_label = 'system_companies'
        managed = True
        # هذا يجعل المودل يظهر في public schema فقط
        default_related_name = '+'

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
# -----------------------------------------------------------
#  ----------------------- انواع الشاحنات----------------------------
# class TrucksTypes(models.Model):
#     manufacturer = models.CharField(max_length=100, verbose_name="الشركه المصنعه")
#     description = models.TextField(verbose_name="الوصف", blank=True, null=True)
#     length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الطول (متر)")
#     width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="العرض (متر)")
#     height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الارتفاع (متر)")
#     status = models.BooleanField(default=True, verbose_name="الحالة")
#     date_of_registration = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

#     class Meta:
#         verbose_name = "نوع الشاحنة"
#         verbose_name_plural = "أنواع الشاحنات"

#     def __str__(self):
#         return self.manufacturer

# -----------------------------------------------------------
#  ----------------------- السائقين----------------------------
class DriverNeme(models.Model):  # السائقين
    driver_name = models.CharField(
    max_length=20, 
    verbose_name="اسم السائق",
    validators=[RegexValidator(
        regex=r'^[a-zA-Z\u0600-\u06FF\s]+$',  
        message="يجب أن يحتوي اسم السائق على أحرف فقط ولا يُسمح بالأرقام."
    )]
    )
    driver_img = models.ImageField(
        upload_to="driver_img/%Y/%m/%d",
        verbose_name="صورة السائق",
    )
    phone_number = models.CharField(max_length=15, default="+967 ",
        validators=[RegexValidator(
            regex=r'^\+?\d{9,15}$',
            message="رقم الهاتف يجب أن يكون بين 9 و 15 رقمًا ويمكن أن يبدأ بعلامة '+'"
        )],
        verbose_name="رقم الهاتف"
        )
    address = models.CharField(max_length=15, verbose_name="العنوان")
    card_number = models.CharField(
    max_length=25,         
    unique=True,
    verbose_name="رقم البطاقة",
        validators=[RegexValidator(
            regex=r'^\d{9,25}$', 
            message=" يجب ان يكون رقم البطاقة بين 9 و 25 رقما ولا يحتوي على رموز."
    )]
    )
    date_of_registration = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    number_of_trucks = models.PositiveIntegerField(verbose_name="عدد الشاحنات")
    class Meta:
        verbose_name = "السائق"
        verbose_name_plural = "السائقيين"
    
    

    def __str__(self):
        return self.driver_name
# -----------------------------------------------------------
#  ----------------------- الشاحانات----------------------------

class Trucks(models.Model):
    plate_number = models.CharField(
        max_length=20, 
        verbose_name="رقم اللوحه",
        unique=True
    )
    
    number_of_axles = models.IntegerField(
        verbose_name="عدد المحاور"
    )
    truck_type = models.CharField(max_length=50, verbose_name="نوع الشاحنه")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    condition = models.BooleanField(default=True, verbose_name="الحالة")
    driver_name = models.ForeignKey(DriverNeme, on_delete=models.CASCADE, verbose_name="اسم السائق")

    class Meta:
        verbose_name = "الشاحنه"
        verbose_name_plural = "الشاحنات"

    def clean(self):
        super().clean()
        # التحقق من وجود وزن قانوني لعدد المحاور
        if not Legal_weight.objects.filter(number_of_axes=self.number_of_axles).exists():
            raise ValidationError(f"لا يوجد وزن قانوني مسجل لشاحنة ذات {self.number_of_axles} محاور")

    def __str__(self):
        return self.plate_number






# -----------------------------------------------------------
#  ----------------------- المواد----------------------------
class Material(models.Model):
    # الفئات المتاحة
    CATEGORY_CHOICES = [
        ('dry', 'المواد الجافة'),
        ('liquid', 'المواد السائلة'),
        ('heavy_machinery', 'الآلات الثقيلة والمركبات'),
        ('containers', 'الحاويات'),
    ]

    # مستويات الخطورة
    HAZARD_LEVEL_CHOICES = [
        ('flammable', 'قابلة للاشتعال'),
        ('toxic', 'سام'),
        ('non_hazardous', 'غير خطرة'),
    ]

    # وحدات القياس
    UNIT_CHOICES = [
        ('ton', 'طن'),
        ('cubic_meter', 'متر مكعب'),
        ('kg', 'كجم'),
        ('piece', 'بالحبة'),
    ]

    # الحقول المطلوبة
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="فئة المادة")
    name_material = models.CharField(max_length=20, verbose_name="الماده")
    description = models.TextField()
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, verbose_name="وحدة القياس")

    # حقل الوزن الموحد (يقبل القيم العشرية أو الصحيحة حسب نوع الوحدة)
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="الوزن",
        help_text="إذا كانت الوحدة (طن، متر مكعب، كجم) أدخل قيمة عشرية، وإذا كانت (بالحبة) أدخل رقماً صحيحاً فقط."
    )
    quantity_mat = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الكمية")

    # الكثافة (تظهر فقط للمواد السائلة)
    density = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="الكثافة",
        help_text="يظهر فقط للمواد السائلة"
    )

    hazard_level = models.CharField(
        max_length=20, choices=HAZARD_LEVEL_CHOICES, blank=True, null=True, verbose_name="مستوى الخطورة"
    )
    date_and_time = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ ووقت الاضافة")
    price_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="السعر لكل وحدة"
    )

    class Meta:
        verbose_name = "الماده"
        verbose_name_plural = " المواد "

    def __str__(self):
        return self.name_material

    def save(self, *args, **kwargs):
        """
        - إذا كانت الفئة مواد سائلة، يجب أن يكون حقل الكثافة غير فارغ.
        - يتم التأكد من أن الوزن متوافق مع وحدة القياس المختارة.
        """
        if self.category != 'liquid':
            self.density = None  # الكثافة متاحة فقط للمواد السائلة

        if self.unit == 'piece':  # إذا كانت الوحدة بالحبة، يجب أن يكون الوزن عددًا صحيحًا
            if self.weight and self.weight % 1 != 0:
                raise ValueError("الوزن بالحبة يجب أن يكون رقمًا صحيحًا فقط.")
        else:  # إذا كانت الوحدة غير الحبة، يجب أن يكون الوزن عشريًا
            if self.weight and self.weight < 0:
                raise ValueError("الوزن يجب أن يكون رقمًا موجبًا.")

        super().save(*args, **kwargs)

# -----------------------------------------------------------
#  ----------------------- الوزن القانوني ----------------------------

# class Legal_weight(models.Model):  # جدول الوزن القانوني
#     legal_weight_L_W = models.DecimalField(max_digits=10, decimal_places=5, default=0.00, verbose_name=" الوزن القانوني")
#     number_of_axes = models.PositiveIntegerField(verbose_name="عدد المحاور")
#     note = models.TextField(default="لا توجد بيانات", help_text="يرجى إدخال وصف المنتج بالتفصيل. ", verbose_name="ملاحظه")
#     registration_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

#     class Meta:
#         verbose_name = "الوزن القانوني"
#         verbose_name_plural = " الوزن القانوني"

#     def __str__(self):
#         return f"{self.legal_weight_L_W}"


# نموذج WeightCard المعدل  docker compose up -d


# -----------------------------------------------------------
#  ----------------------- بطاقات الوزن ----------------------------



class WeightCard(models.Model):
    STATUS_CHOICES = [
        ('incomplete', 'بطاقة غير مكتملة '),
        ('complete', 'بطاقة مكتملة '),
    ]

    plate_number = models.ForeignKey(Trucks, on_delete=models.CASCADE, verbose_name="رقم اللوحة")
    empty_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الفارغ", null=True, blank=True)
    loaded_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن المحمل", null=True, blank=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الصافي", null=True, blank=True)
    driver_name = models.ForeignKey(DriverNeme, on_delete=models.CASCADE, verbose_name="اسم السائق", null=True, blank=True)
    entry_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الدخول")
    exit_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الخروج")
    # quantity = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الكمية", null=True, blank=True)
    # material =  materials_data = models.JSONField(null=True, blank=True, verbose_name="المواد والكميات")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='incomplete', verbose_name="حالة البطاقة")

    class Meta:
        verbose_name = " بطاقة الوزن"
        verbose_name_plural = " بطاقات الوزن"
    

    def clean(self):
        # errors = {}
        if not self.empty_weight:
            self.status = 'incomplete'
            raise ValidationError("يجب إدخال رقم اللوحة، الوزن الفارغ، وتاريخ الدخول!")

        if self.loaded_weight and self.empty_weight:
            if self.loaded_weight < self.empty_weight:
                raise ValidationError("🚫 الوزن المحمل لا يمكن أن يكون أقل من الوزن الفارغ!")

        # if self.loaded_weight:
        #     if not self.materials.exists():  # ✅ تحقق من وجود مواد مرتبطة
        #         raise ValidationError("❌ يجب إدخال مادة واحدة على الأقل عند إدخال الوزن المحمل.")
                
        
        # if self.materials:
        #     if not self.loaded_weight:
        #         raise ValidationError("يجب ادخال الوزن المحمل عند ادخال الماده والكميه ❌")

    def save(self, *args, **kwargs):
        # self.clean()


        

        if self.plate_number:
            self.driver_name = self.plate_number.driver_name

        if self.empty_weight and not self.entry_date:
            self.entry_date = now()

        if self.loaded_weight and not self.exit_date:
            self.exit_date = now()

        if self.empty_weight and self.loaded_weight:
            self.net_weight = self.loaded_weight - self.empty_weight
            self.status = 'complete'
            self.exit_date = now()

        # إذا أصبحت البطاقة مكتملة، ننشئ الفاتورة
        if self.status == 'complete':
            from system_companies.models import Invoice, InvoiceMaterial  # تأكد من الاستيراد
            invoice, created = Invoice.objects.get_or_create(
                weight_card=self,
                defaults={'net_weight': self.net_weight}
            )

            if not created:
                invoice.net_weight = self.net_weight
                invoice.save()

            # نحذف المواد القديمة وننسخ المواد المرتبطة
            for item in self.materials.all():
                material = getattr(item, 'material', None)
                if not material or item.quantity is None:
                    continue  # تجاهل الإدخالات غير المكتملة

                try:
                    InvoiceMaterial.objects.create(
                        invoice=invoice,
                        material=material,
                        quantity=item.quantity
                    )
                except Exception as e:
                    # تسجيل الخطأ إن أردت
                    print(f"خطأ أثناء إنشاء مادة الفاتورة: {e}")
                    continue




        # نحفظ بطاقة الوزن أولًا
        super().save(*args, **kwargs)

        # بعد الحفظ، ننشئ المخالفة إن وجدت
        if self.empty_weight and self.loaded_weight:
            try:
                legal_weight_entry = Legal_weight.objects.get(number_of_axes=self.plate_number.number_of_axles)
                legal_weight = legal_weight_entry.legal_weight_L_W

                if self.loaded_weight > legal_weight:
                    excess_weight = self.loaded_weight - legal_weight  # بافتراض أن الوزن بالأطنان

                    try:
                        violation_type = ViolationsType.objects.get(name="Exceeding the legal weight")
                        penalty = excess_weight * violation_type.penalty_amount

                        from system_companies.models import ViolationRecord
                        if not ViolationRecord.objects.filter(weight_card_vio=self).exists():
                            ViolationRecord.objects.create(
                                plate_number_vio=self.plate_number,
                                violation_type=violation_type,
                                weight_card_vio=self,
                                device_vio=None,
                                entry_exit_log=None,
                                image_violation=None
                            )
                    except ViolationsType.DoesNotExist:
                        pass

            except Legal_weight.DoesNotExist:
                pass


        super().save(*args, **kwargs)




# -----------------------------------------------------------
#  ----------------------- الفواتير----------------------------
# نموذج Invoice المعدل
class Invoice(models.Model):
    weight_card = models.ForeignKey(WeightCard, on_delete=models.CASCADE, verbose_name="رقم بطاقة الوزن", unique=True)
    datetime = models.DateTimeField(auto_now_add=True, verbose_name="التاريخ والوقت")
    net_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الصافي", editable=True)

    class Meta:
        verbose_name = "الفاتورة"
        verbose_name_plural = "الفواتير"
# --------------------api------------
        db_table = 'system_companies_invoice'  # تأكد أن الاسم مطابق لما في DB

#-----------------api_end--------------

    def __str__(self):
        return f"فاتورة {self.id} - {self.weight_card}"



# إشعار post_save المعدل


# @receiver(post_save, sender=WeightCard)
# def create_or_update_invoice(sender, instance, **kwargs):
#     if instance.status == 'complete':
#         # إنشاء أو تحديث الفاتورة
#         invoice, created = Invoice.objects.get_or_create(
#             weight_card=instance,
#             defaults={'net_weight': instance.net_weight}
#         )

#         if not created:
#             invoice.net_weight = instance.net_weight
#             invoice.save()

#         # حذف المواد القديمة المرتبطة بالفاتورة (في حال كانت عملية تحديث)
#         invoice.invoice_materials.all().delete()

#         # نسخ كل المواد من بطاقة الوزن إلى الفاتورة
#         # استخدم العلاقة materials التي تم تعريفها في WeightCardMaterial
#         for weight_card_material in instance.materials.all():
#             InvoiceMaterial.objects.create(
#                 invoice=invoice,
#                 material=weight_card_material.material,
#                 quantity=weight_card_material.quantity
#             )

# -----------------------------------------------------------
#  ----------------------- الفواتير----------------------------
class InvoiceMaterial(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_materials')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=5)

    def __str__(self):
        return f"{self.material.name_material} - {self.quantity}"
# -----------------------------------------------------------
# -----------------------------------------------------------
class WeightCardMaterial(models.Model):
    weight_card = models.ForeignKey(
        'WeightCard',
        on_delete=models.CASCADE,
        related_name='materials',  # ✅ هذا مهم لتسهيل الوصول من الجهة العكسية
        verbose_name="بطاقة الوزن"
    )
    material = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="المادة")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية")

    class Meta:
        verbose_name = "مادة مرتبطة"
        verbose_name_plural = "المواد المرتبطة"
    
    def clean(self):
        # هذا ينفذ عند التحقق من الفورم (في Django Admin أو ModelForm)
        if not self.pk and self.material and self.quantity:
            if self.material.quantity_mat < self.quantity:
                raise ValidationError(
                    f"❌ الكمية المطلوبة ({self.quantity}) أكبر من الكمية المتوفرة ({self.material.quantity_mat}) في المادة ({self.material.name_material})"
                )
        
            # تحقق أن الوزن المحمل موجود إن تم إدخال مادة
        if self.quantity and not self.weight_card.loaded_weight:
            raise ValidationError("❌ يجب إدخال الوزن المحمل قبل إدخال المادة.")


    def save(self, *args, **kwargs):
        self.full_clean()  # هذا يستدعي clean() تلقائيًا قبل الحفظ
        if not self.pk:
            self.material.quantity_mat -= self.quantity
            self.material.save()
        super().save(*args, **kwargs)


#  ----------------------- الاتصال----------------------------



# جدول الاتصال
# class Connection(models.Model):
#     CONNECTION_TYPES = [
#         ('USB', 'USB'),
#         ('WiFi', 'WiFi'),
#         ('Serial', 'Serial'),
#         ('API', 'API')
#     ]
    
#     connection_name = models.CharField(max_length=10, choices=CONNECTION_TYPES, verbose_name="نوع الاتصال")
#     date_and_tim = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

#     class Meta:
#         verbose_name = "الاتصال"
#         verbose_name_plural = "الاتصالات"

#     def __str__(self):
#         return self.connection_name
# -----------------------------------------------------------
#  ----------------------- الاجهزه----------------------------


# def validate_ip_address(ip):
#     if not is_camera_reachable(ip):
#         raise ValidationError(f"لا يمكن الوصول إلى الجهاز عبر IP: {ip}")
# def validate_camera_stream(ip):
#     if not is_camera_streaming(ip):
#         raise ValidationError(f"الكاميرا عبر IP {ip} غير متاحة للبث!")
# def validate_serial_connection(port):
#     if not is_serial_device_available(port):
#         raise ValidationError(f"الجهاز غير متصل بالمنفذ {port}")

# class Devices(models.Model):

#     CONNECTION_TYPES = [
#         ('wifi', 'WiFi'),
#         ('serial', 'Serial'),
#     ]

#     name_devices = models.CharField(max_length=20, verbose_name="اسم الجهاز")
#     installation_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التثبيت")
#     address_ip = models.GenericIPAddressField(verbose_name="عنوان IP", validators=[validate_ip_address and validate_camera_stream and validate_serial_connection])

#     device_status = models.BooleanField(default=True, verbose_name="حالة الجهاز")
#     location = models.CharField(max_length=20, verbose_name="موقع الجهاز")
    
#     # تعيين اتصال افتراضي
#     connection_type = models.CharField(max_length=10, choices=CONNECTION_TYPES, verbose_name="نوع الاتصال")

#     class Meta:
#         verbose_name = "الجهاز"
#         verbose_name_plural = "الأجهزة"

#     def __str__(self):
#         return f"{self.name_devices} ({self.address_ip})"

# -----------------------------------------------------------
#  -----------------------  اعدادات الاجهزه----------------------------

class Devices(models.Model):

    NAME_DENICES = [
        ('camera_1', 'كاميرا دخول'),
        ('camera_2', 'كاميرا ميزان 1 '),
        ('camera_3', 'كاميرا ميزان 2'),
        ('camera_4', 'كاميرا خروج '),
        ('denice_weight_1', 'جهاز وزن 1'),
        ('denice_weight_2', 'جهاز وزن 2'),
    ]

    CONNECTION_TYPES = [
        ('wifi', 'WiFi'),
        ('serial', 'Serial'),
    ]

    LOCARION = [
        ('entry','دخول'),
        ('exit','خروج'),
        ('امام الميزان 1','امام الميزان 1'),
        ('امام الميزان 2','امام الميزان 2'),

    ]

    BAUD_RATE_CHOICES = [
        ('9600', '9600'),
        ('19200', '19200'),
        ('38400', '38400'),
        ('57600', '57600'),
        ('115200', '115200')
    ]

    INITIALIZATION_DATA_SIZE = [
        ( 5, '5'),
        ( 6, '6'),
        ( 7, '7'),
        ( 8, '8'),
    ]

    NUMBER_OF_INITIALIZATION_BITS = [
        ( 1, '1'),
        ( 2, '2'),
       
    ]

    name_devices = models.CharField(max_length=20, choices=NAME_DENICES, verbose_name="اسم الجهاز")
    address_ip = models.GenericIPAddressField(verbose_name="عنوان IP")
    connection_type = models.CharField(max_length=10, choices=CONNECTION_TYPES, verbose_name="نوع الاتصال")
    device_status = models.BooleanField(default=True, verbose_name="حالة الجهاز")
    location = models.CharField(max_length=20, choices=LOCARION, verbose_name="موقع الجهاز")
    port_number = models.CharField(max_length=50, verbose_name="رقم المنفذ", default="COM1")
    baud_rate = models.CharField(max_length=50, choices=BAUD_RATE_CHOICES, verbose_name="معدل الباود", default="9600")
    initialization_data_size = models.PositiveIntegerField(choices=INITIALIZATION_DATA_SIZE,verbose_name="حجم بيانات التهيئة",default=8)
    number_of_initialization_bits = models.PositiveIntegerField(choices=NUMBER_OF_INITIALIZATION_BITS,verbose_name="عدد بتات التهيئة",default=1)
    parity_type = models.CharField(max_length=10, choices=[('None', 'None'), ('Even', 'Even'), ('Odd', 'Odd')], verbose_name="نوع التماثل",default='None')
    flow_control = models.CharField(max_length=20, choices=[('None', 'None'), ('XON/XOFF', 'XON/XOFF'), ('RTS/CTS', 'RTS/CTS')], verbose_name="التحكم بالتدفق",default='None')
    number_of_digits_after_decimal_point = models.PositiveSmallIntegerField(verbose_name="عدد الأرقام بعد العلامة العشرية", default=2)
    last_date_settings_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تاريخ لتحديث الإعدادات")
    username = models.CharField(max_length=100, verbose_name="اسم المستخدم", blank=True, null=True)
    password = models.CharField(max_length=100, verbose_name="كلمة المرور", blank=True, null=True)

    class Meta:
        verbose_name = " الجهاز"
        verbose_name_plural = " الأجهزة"

    def get_camera_stream_url(self):
        """ إرجاع رابط بث الكاميرا بناءً على نوع الاتصال """
        if self.connection_type == "wifi" and self.address_ip:
            return f"http://{self.address_ip}:8080/video"  # بث MJPEG عبر HTTP
        return None


    def check_camera_connection(self):
        """
        التحقق من الاتصال بالجهاز وتطبيق الإعدادات تلقائيًا.
        تُرجع True إذا نجح الاتصال، و False إذا فشل.
        """
        if self.connection_type == "wifi" and self.address_ip:
            # تطبيق إعدادات WiFi (لا تحتاج إلى إعدادات خاصة)
            print(f"تطبيق إعدادات WiFi للجهاز {self.name_devices}")
            url = self.get_camera_stream_url()

            # التحقق من الاتصال بالكاميرا عبر WiFi
            cap = cv2.VideoCapture(self.get_camera_stream_url())
            if cap.isOpened():
                cap.release()
                print("تم الاتصال بالكاميرا بنجاح!")
                return True
            else:
                print("فشل الاتصال بالكاميرا!")
                return False

        elif self.connection_type == "serial" and self.port_number:
            # تطبيق إعدادات الاتصال التسلسلي
            try:
                ser = serial.Serial(
                    port=self.port_number,
                    baudrate=int(self.baud_rate),
                    bytesize=int(self.initialization_data_size),
                    parity=self.parity_type[0],  # 'N', 'E', 'O'
                    stopbits=int(self.number_of_initialization_bits),
                    timeout=2
                )
                print(f"تم تطبيق إعدادات الاتصال التسلسلي للجهاز {self.name_devices}")

                # التحقق من الاتصال بالجهاز التسلسلي
                if ser.is_open:
                    ser.close()
                    print("تم الاتصال بالجهاز التسلسلي بنجاح!")
                    return True
                else:
                    print("فشل الاتصال بالجهاز التسلسلي!")
                    return False

            except serial.SerialException as e:
                print(f"فشل تطبيق إعدادات الاتصال التسلسلي: {e}")
                return False

        else:
            print("نوع الاتصال غير مدعوم أو الإعدادات غير كافية!")
            return False

    def clean(self):
        """
        التحقق من البورت المشغول واتصال الجهاز قبل الحفظ.
        """
        # التحقق من البورت المشغول
        if self.connection_type == "serial":
            existing_device = Devices.objects.filter(port_number=self.port_number).exclude(pk=self.pk).first()
            if existing_device:
                raise ValidationError({"port_number": "البورت مشغول بالفعل بجهاز آخر!"})

        # التحقق من اتصال الجهاز
        if not self.check_camera_connection():
            raise ValidationError("فشل الاتصال بالجهاز! يرجى التحقق من الإعدادات.")

    def save(self, *args, **kwargs):
        """
        التحقق من صحة البيانات قبل الحفظ.
        """
        self.clean()  # استدعاء دالة clean للتحقق من البورت المشغول واتصال الجهاز
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_devices} ({self.address_ip if self.address_ip else self.port_number})"
 

 # -----------------------------------------------------------
#  ----------------------- عمليات الدخول ----------------------------
class Entry_and_exit(models.Model):
    NAME = [
        ("process_entry", 'عملية دخول'),
        ("process_exit", 'عملية خروج'),
    ]
    STATUS_PRUSS = [
        ("complete", 'مكتمله'),
        ("incomplete", 'غير مكتمل'),
    ]
    
    name = models.CharField(max_length=50, choices=NAME, verbose_name="العمليه")
    device = models.ForeignKey(Devices, on_delete=models.CASCADE, verbose_name="الكاميرا", null=True, blank=True)
    plate_number_E_e = models.ForeignKey(Trucks, on_delete=models.CASCADE, verbose_name="رقم اللوحه")
    image_path_entry = models.ImageField(upload_to="entry_images/%y/%m/%d", verbose_name="صور الدخول", null=True, blank=True)
    image_path_exit = models.ImageField(upload_to="exit_images/%y/%m/%d", verbose_name="صور الخروج", null=True, blank=True)
    entry_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الدخول")
    exit_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الخروج")
    pruss_status = models.CharField(max_length=10, choices=STATUS_PRUSS, default='incomplete', verbose_name="حالة البطاقة")

    class Meta:
        verbose_name = "عمليات الدخول الخروج"
        verbose_name_plural = "عمليات الدخول الخروج"
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.plate_number_E_e}"

    def entry_image_tag(self):
        if self.image_path_entry:
            return mark_safe(f'<img src="{self.image_path_entry.url}" style="width: 100px; height: auto;" />')
    entry_image_tag.short_description = "صورة الدخول"

    def exit_image_tag(self):
        if self.image_path_exit:
            return mark_safe(f'<img src="{self.image_path_exit.url}" style="width: 100px; height: auto;" />')
    exit_image_tag.short_description = "صورة الخروج"

    def save(self, *args, **kwargs):
        # تحديد نوع العملية تلقائياً بناءً على الصور
        if self.image_path_entry and not self.image_path_exit:
            self.name = "process_entry"
        elif self.image_path_exit:
            self.name = "process_exit"
        
        # تسجيل وقت الدخول عند إضافة صورة الدخول
        if self.image_path_entry and not self.entry_date:
            self.entry_date = timezone.now()
        
        # تسجيل وقت الخروج عند إضافة صورة الخروج
        if self.image_path_exit and not self.exit_date:
            self.exit_date = timezone.now()
        
        # تحديث حالة العملية
        self.update_status()
        
        super().save(*args, **kwargs)
    
    def update_status(self):
        """تحديث حالة العملية تلقائياً"""
        if self.image_path_entry and self.image_path_exit and self.entry_date and self.exit_date:
            self.pruss_status = "complete"
        else:
            self.pruss_status = "incomplete"
    
# -----------------------------------------------------------
#  ------------------------المخالفات ----------------------------
class ViolationRecord(models.Model):
    plate_number_vio = models.ForeignKey(Trucks, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رقم اللوحه")
    violation_type = models.ForeignKey("companies_manager.ViolationsType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name=" نوع المخالفة")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ ووقت المخالفة")
    device_vio = models.ForeignKey(Devices, on_delete=models.CASCADE, verbose_name="الكاميرا",null=True, blank=True )
    entry_exit_log = models.ForeignKey(Entry_and_exit, on_delete=models.CASCADE, verbose_name="العمليه")
    weight_card_vio = models.ForeignKey(WeightCard, on_delete=models.CASCADE, verbose_name="بطاقة الوزن")
    image_violation = models.ImageField(upload_to="images_violation/%y/%m/%d", verbose_name="صور المخالفة", null=True, blank=True)
    device_vio = models.ForeignKey(Devices, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الكاميرا",)
    entry_exit_log = models.ForeignKey(Entry_and_exit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="العمليه")
    weight_card_vio = models.ForeignKey(WeightCard, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="بطاقة الوزن")
    image_violation = models.ImageField(upload_to="images_violation/%y/%m/%d", verbose_name="صور المخالفة")

    class Meta:
        verbose_name = " المخالفه"
        verbose_name_plural = "المخالفات"
    
    def images_violation_tag(self):
        if self.image_violation:
            return mark_safe(f'<img src="{self.image_violation.url}" style="width: 100px; height: auto;" />')

    images_violation_tag.short_description = "صور المخالفة"

    def __str__(self):
        return str(self.plate_number_vio.plate_number)
    
    def get_penalty_amount(self):
    # الوصول إلى حقل الغرامة من نوع المخالفة
        return self.violation_type.penalty_amount if self.violation_type else None
    
    def get_driner_name(self):
        return f"{self.plate_number_vio.driver_name}"
    
    get_driner_name.short_description = 'السائق'


    





#  ------------------------الدوام----------------------------
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'موجود ✅'),
        ('absent', 'غير موجود ❌'),
    ]

    SHIFT_CHOICES = [
        ('morning', 'صباحي 🌞'),
        ('night', 'ليلي 🌙'),
    ]

    date = models.DateField(default=now, verbose_name="التاريخ")
    check_in_time = models.TimeField(null=True, blank=True, verbose_name="وقت الدخول")
    check_out_time = models.TimeField(null=True, blank=True, verbose_name="وقت الخروج")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present', verbose_name="الحالة")
    shift_type = models.CharField(max_length=10, choices=SHIFT_CHOICES, default='morning', verbose_name="نوع الدوام")
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "سجل الدوام"
        verbose_name_plural = "سجلات الدوام"

   

    def __str__(self):
        return self.date # ✅ تصحيح خطأ في `usermame` إلى `username`
        return self.date # ✅ تصحيح خطأ في `usermame` إلى `username`



# -----------------------------------------------------------
class ReportPermission(models.Model):
    class Meta:
        managed = False  # لن يتم إنشاء جدول في قاعدة البيانات
        default_permissions = ()  # إزالة create/change/delete الافتراضية
        permissions = [
            ('can_view_reports_page', 'Can view Reports Page'),
        ]
        verbose_name = 'Reports Page Access'
        verbose_name_plural = 'Reports Page Access'
