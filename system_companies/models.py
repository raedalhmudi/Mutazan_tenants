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
from django.conf import settings
# from companies_manager.models import Company, ViolationsType
import cv2
import socket
import serial.tools.list_ports
import serial
# from user_management.models import CustomUser

# User = CustomUser 
# from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
# from django.contrib.auth.models import AbstractUser

# class CustomUser(AbstractUser):
#     profile_picture = models.ImageField(
#         upload_to="profile_pictures/%Y/%m/%d", 
#         blank=True, 
#         null=True, 
#         verbose_name="الصورة الشخصية"
#     )
#     phone_number = models.CharField(
#         max_length=15, 
#         blank=True, 
#         null=True, 
#         verbose_name="رقم الهاتف"
#     )
#     address = models.CharField(
#         max_length=255, 
#         blank=True, 
#         null=True, 
#         verbose_name="عنوان السكن"
#     )
#     is_company_admin = models.BooleanField(default=False)  # يحدد ما إذا كان المستخدم مديرًا أم لا


# -----------------------------------------------------------
#  ----------------------- انواع الشاحنات----------------------------
class TrucksTypes(models.Model):
    manufacturer = models.CharField(max_length=100, verbose_name="الشركه المصنعه")
    description = models.TextField(verbose_name="الوصف", blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الطول (متر)")
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="العرض (متر)")
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الارتفاع (متر)")
    status = models.BooleanField(default=True, verbose_name="الحالة")
    date_of_registration = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    class Meta:
        verbose_name = "نوع الشاحنة"
        verbose_name_plural = "أنواع الشاحنات"

    def __str__(self):
        return self.manufacturer

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
    phone_number = models.CharField(max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?\d{9,15}$',
            message="رقم الهاتف يجب أن يكون بين 9 و 15 رقمًا ويمكن أن يبدأ بعلامة '+'"
        )],
        verbose_name="رقم الهاتف"
        )
    address = models.CharField(max_length=15, verbose_name="العنوان")
    card_number = models.CharField(
    max_length=25, 
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

class Trucks(models.Model):  # الشاحنات
    plate_number = models.CharField(
    max_length=20, 
    verbose_name="رقم اللوحه",
    unique=True
    )
    truck_type = models.ForeignKey(TrucksTypes, on_delete=models.CASCADE, verbose_name="نوع الشاحنه")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    condition = models.BooleanField(default=True, verbose_name="الحالة")
    driver_name = models.ForeignKey(DriverNeme, on_delete=models.CASCADE, verbose_name="اسم السائق")

    class Meta:
        verbose_name = "الشاحنه"
        verbose_name_plural = "الشاحنات"

    def __str__(self):
        return self.plate_number


# -----------------------------------------------------------
#  ----------------------- المستخدمين----------------------------

# ✅ إنشاء نموذج المستخدم المخصص
# class CustomUser(AbstractUser):
#     address = models.CharField(max_length=50, verbose_name="العنوان")
#     phone_number = models.CharField(
#         max_length=15,
#         validators=[RegexValidator(
#             regex=r'^\+?\d{9,15}$',
#             message="رقم الهاتف يجب أن يكون بين 9 و 15 رقمًا ويمكن أن يبدأ بعلامة '+'"
#         )],
#         verbose_name="رقم الهاتف"
#     )
#     image = models.ImageField(upload_to="user_company_images/%y/%m/%d", verbose_name="الصورة")

#     # ✅ حل مشكلة التعارض بإضافة related_name جديد
#     groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
#     user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

#     def __str__(self):
#         return self.username




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

class Legal_weight(models.Model):  # جدول الوزن القانوني
    manufacturer_L_W = models.ForeignKey(TrucksTypes, on_delete=models.CASCADE, verbose_name="نوع الشاحنه")
    the_material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="الماده")
    legal_weight_L_W = models.DecimalField(max_digits=10, decimal_places=5, default=0.00, verbose_name=" الوزن القانوني")
    number_of_axes = models.PositiveIntegerField(verbose_name="عدد المحاور")
    note = models.TextField(default="لا توجد بيانات", help_text="يرجى إدخال وصف المنتج بالتفصيل.", verbose_name="ملاحظه")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    class Meta:
        verbose_name = "الوزن القانوني"
        verbose_name_plural = " الوزن القانوني"

    def __str__(self):
        return f"{self.manufacturer_L_W.manufacturer}"


# نموذج WeightCard المعدل  docker compose up -d

# -----------------------------------------------------------
#  ----------------------- بطاقات الوزن ----------------------------
class WeightCard(models.Model):
    STATUS_CHOICES = [
        ('incomplete', 'بطاقة غير مكتملة ❌'),
        ('complete', 'بطاقة مكتملة ✅'),
    ]
    plate_number = models.ForeignKey(Trucks, on_delete=models.CASCADE, verbose_name="رقم اللوحة")
    empty_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الفارغ", null=True, blank=True)
    loaded_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن المحمل", null=True, blank=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الصافي", null=True, blank=True)
    driver_name = models.ForeignKey(DriverNeme, on_delete=models.CASCADE, verbose_name="اسم السائق", null=True, blank=True)
    entry_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الدخول")
    exit_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الخروج")
    quantity = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الكمية", null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="المادة", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='incomplete', verbose_name="حالة البطاقة")

    class Meta:
        verbose_name = " بطاقة الوزن"
        verbose_name_plural = " بطاقات الوزن"

    def clean(self):
        # التحقق من إدخال البيانات الأساسية
        if not self.empty_weight :
            self.status = 'incomplete'
            raise ValidationError("يجب إدخال رقم اللوحة، الوزن الفارغ، وتاريخ الدخول!")
        

        if self.loaded_weight and self.empty_weight:
            if self.loaded_weight < self.empty_weight:
                raise ValidationError("🚫 الوزن المحمل لا يمكن أن يكون أقل من الوزن الفارغ!")


        # إذا تم إدخال الوزن المحمل، تحقق من الوزن القانوني
        if self.loaded_weight:
            if not self.driver_name or not self.material or not self.quantity:
                self.status = 'incomplete'
                raise ValidationError("يجب إدخال اسم السائق، المادة، والكمية لإكمال البطاقة!")

            # البحث عن الوزن القانوني للشاحنة والمادة
            try:
                legal_weight_entry = Legal_weight.objects.get(
                    manufacturer_L_W=self.plate_number.truck_type,  # نوع الشاحنة
                    the_material=self.material  # المادة
                )
                
                legal_weight = legal_weight_entry.legal_weight_L_W  # الوزن القانوني
                
                if self.loaded_weight > legal_weight:
                    raise ValidationError(f"🚨 تم تجاوز الوزن القانوني! الوزن القانوني هو {legal_weight} طن، لكن الوزن المحمل {self.loaded_weight} طن.")
            except Legal_weight.DoesNotExist:
                raise ValidationError("⚠️ لا يوجد وزن قانوني مسجل لهذا النوع من الشاحنات والمادة. يرجى التحقق من البيانات.")

    def save(self, *args, **kwargs):
        self.clean()  # التأكد من التحقق قبل الحفظ
        
        # جلب اسم السائق تلقائياً عند اختيار رقم اللوحة
        if self.plate_number:
            self.driver_name = self.plate_number.driver_name
        
        if self.empty_weight and not self.entry_date:
            self.entry_date = now()

        # تسجيل وقت الخروج عند إدخال الوزن المحمل لأول مرة
        if self.loaded_weight and not self.exit_date:
            self.exit_date = now()
        
        # إذا تم إدخال الوزن المحمل، احسب الوزن الصافي
        if self.empty_weight and self.loaded_weight:
            self.net_weight = self.loaded_weight - self.empty_weight
            self.status = 'complete'
            self.exit_date = now()
        
        super().save(*args, **kwargs)



# -----------------------------------------------------------
#  ----------------------- الفواتير----------------------------
# نموذج Invoice المعدل
class Invoice(models.Model):  # الفواتير
    weight_card = models.ForeignKey(WeightCard, on_delete=models.CASCADE, verbose_name="رقم بطاقة الوزن", default=1, editable=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="الماده")
    quantity = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الكمية", null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True, verbose_name="التاريخ والوقت")
    net_weight = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="الوزن الصافي", editable=True)

    class Meta:
        verbose_name = "الفاتوره"
        verbose_name_plural = "الفواتير"

    def __str__(self):
        return f"فاتورة {self.id} - {self.weight_card}"


# إشعار post_save المعدل
@receiver(post_save, sender=WeightCard)
def create_invoice(sender, instance, created, **kwargs):
    """
    يتم إنشاء الفاتورة فقط عند اكتمال بطاقة الوزن
    """
    # إذا كانت البطاقة مكتملة ولم يكن هناك فاتورة مرتبطة بها مسبقًا
    if instance.status == 'complete' and not Invoice.objects.filter(weight_card=instance).exists():
        Invoice.objects.create(
            weight_card=instance,
            material=instance.material,
            quantity=instance.quantity,
            net_weight=instance.net_weight,
        )
        
@receiver(post_save, sender=WeightCard)
def update_or_create_invoice(sender, instance, created, **kwargs):
    """
    يتم إنشاء أو تحديث الفاتورة تلقائيًا عند تعديل بطاقة الوزن.
    """
    # إذا كانت البطاقة مكتملة
    if instance.status == 'complete':
        invoice, created_invoice = Invoice.objects.get_or_create(weight_card=instance)

        # في حال تم تعديل البطاقة، نحدث الفاتورة المرتبطة
        invoice.material = instance.material
        invoice.quantity = instance.quantity
        invoice.net_weight = instance.net_weight
        invoice.save()


# -----------------------------------------------------------
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
class Entry_and_exit(models.Model):  # جدول عمليات الدخول والخروج
    NAME = [
        ( "process_entry", 'عملية دخول'),
        ( "process_exit", 'عملية خروج'),
       
    ]
    name = models.CharField(max_length=50, choices=NAME, verbose_name="العمليه")
    device = models.ForeignKey(Devices, on_delete=models.CASCADE, verbose_name="الكاميرا",null=True, blank=True)
    plate_number_E_e = models.ForeignKey(Trucks, on_delete=models.CASCADE, verbose_name="رقم اللوحه")
    image_path_entry = models.ImageField(upload_to="entry_images/%y/%m/%d", verbose_name="صور الدخول")
    image_path_exit = models.ImageField(upload_to="exit_images/%y/%m/%d", verbose_name="صور الخروج",null=True, blank=True)
    entry_date = models.DateTimeField(auto_now_add=True)
    exit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عمليات الدخول الخروج"
        verbose_name_plural = "  عمليات الدخول الخروج"
    def __str__(self):
        return f"{self.name}"

    def entry_image_tag(self):
        if self.image_path_entry:
            return mark_safe(f'<img src="{self.image_path_entry.url}" style="width: 100px; height: auto;" />')

    entry_image_tag.short_description = "صورة الدخول"

    def exit_image_tag(self):
        if self.image_path_exit:
            return mark_safe(f'<img src="{self.image_path_exit.url}" style="width: 100px; height: auto;" />')

    exit_image_tag.short_description = "صورة الخروج"

    def save(self, *args, **kwargs):
        self.clean()  # التأكد من التحقق قبل الحفظ
        

        if self.image_path_entry and not self.entry_date:
            self.entry_date = now()

        # تسجيل وقت الخروج عند إدخال الوزن المحمل لأول مرة
        if self.image_path_exit and not self.exit_date:
            self.exit_date = now()
      
        super().save(*args, **kwargs)

    
# -----------------------------------------------------------
#  ------------------------المخالفات ----------------------------
class ViolationRecord(models.Model):
    plate_number_vio = models.ForeignKey(Trucks, on_delete=models.CASCADE, verbose_name="رقم اللوحه")
    violation_type = models.ForeignKey("companies_manager.ViolationsType", on_delete=models.CASCADE, verbose_name=" نوع المخالفة")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ ووقت المخالفة")
    device_vio = models.ForeignKey(Devices, on_delete=models.CASCADE, verbose_name="الكاميرا",null=True, blank=True )
    entry_exit_log = models.ForeignKey(Entry_and_exit, on_delete=models.CASCADE, verbose_name="العمليه")
    weight_card_vio = models.ForeignKey(WeightCard, on_delete=models.CASCADE, verbose_name="بطاقة الوزن")
    image_violation = models.ImageField(upload_to="images_violation/%y/%m/%d", verbose_name="صور المخالفة")

    class Meta:
        verbose_name = " المخالفه"
        verbose_name_plural = "المخالفات"

    def __str__(self):
        return str(self.plate_number_vio.plate_number)



# -----------------------------------------------------------
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

    # def calculate_total_hours(self):
    #     """حساب عدد ساعات العمل تلقائيًا عند تسجيل الخروج"""
    #     if self.check_in_time and self.check_out_time:
    #         from datetime import datetime
    #         fmt = "%H:%M:%S"
    #         in_time = datetime.strptime(str(self.check_in_time), fmt)
    #         out_time = datetime.strptime(str(self.check_out_time), fmt)
    #         total = out_time - in_time
    #         self.total_hours = round(total.total_seconds() / 3600, 2)
    
    # def save(self, *args, **kwargs):
    #     self.calculate_total_hours()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.date # ✅ تصحيح خطأ في `usermame` إلى `username`


