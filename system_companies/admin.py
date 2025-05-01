from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe
from .models import *
from Mutazan_weight.base_admin import BaseAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.utils.timezone import localtime
from django.db.models import Q
from django.db import models
from django_tenants.utils import get_tenant, get_tenant_model
from .models import UserProfile  # هذا UserProfile تبع الشركة
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# -----------------------------------------
class BaseAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('common/css/system_companies/admin_styles.css',)  # تحديد مكان ملف CSS
        }
    """فلترة أي ForeignKey يشير إلى جدول يحتوي على الحقل condition=True فقط."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """فلترة العلاقات الخارجية (ForeignKey) بناءً على وجود حقل condition في النموذج المرتبط."""
        related_model = db_field.related_model  # جلب الموديل المرتبط بـ FK
        
        # التأكد من أن الجدول يحتوي على الحقل 'condition' ثم تطبيق الفلترة
        if related_model and hasattr(related_model, 'condition'):
            kwargs["queryset"] = related_model.objects.filter(condition=True)  # جلب العناصر المتاحة فقط
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:{}_{}_delete'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        
        return format_html(
            '<a href="{}" class="mr-2 btn-icon btn-icon-only btn btn-outline-info " style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> </a>'
            '<a href="{}" class="mr-2 btn-icon btn-icon-only btn btn-outline-danger">'
            '<i class="fas fa-trash"></i> </a>',
            edit_url, delete_url
        )

    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

    def status_badge(self, obj):
        """عرض الحالة كشارة (Badge) في Django Admin بالتنسيق المطلوب"""
        if obj.status:
            # متاح
            # color = "green"
            status_text = "متاح" 
            class_name = "status-badge status-completed"
        else:
            # غير متاح
            # color = "red"
            status_text = "غير متاح" 
            class_name = "status-badge status-pending"

        return format_html(
            f'<span class="{class_name}" {class_name}; padding:4px 8px; border-radius:5px;">{status_text}</span>'
        )
    
    def status_complet(self, obj):
        """عرض الحالة كشارة (Badge) في Django Admin بالتنسيق المطلوب"""
        if obj.status:
            # متاح
            # color = "green"
            status_text = "مكتمل"
            class_name = "status-badge status-completed"
        else:
            # غير متاح
            # color = "red"
            status_text = "غير مكتمل "
            class_name = "status-badge status-pending"

        return format_html(
            f'<span class="{class_name}" {class_name}; padding:4px 8px; border-radius:5px;">{status_text}</span>'
        )

    status_complet.short_description = "الحالة"

    def dimensions(self, obj):
        """عرض الأبعاد بتنسيق منسق"""
        return f"{obj.length} × {obj.width} × {obj.height} متر"

    dimensions.short_description = "الأبعاد"

    def progress_bar(self, obj):
        """إضافة شريط تقدم يعكس الطول نسبة إلى 10 أمتار"""
        max_length = 10  # نفترض أن 10 أمتار هو الحد الأقصى
        progress = (obj.length / max_length) * 100
        color = "success" if progress > 70 else "warning" if progress > 40 else "danger"
        
        return format_html(
            f'''
            <div style="width:120px; background-color:#eee; border-radius:5px; overflow:hidden;">
                <div style="width:{progress}%; background-color:{color}; height:10px; border-radius:5px;"></div>
            </div>
            '''
        )

    progress_bar.short_description = "تقدم (الطول)"
# -----------------------------------------------------
class CompanyGroupAdmin(BaseAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'permissions' in form.base_fields:
            # فلترة الصلاحيات لتبقي فقط تلك الخاصة بتطبيق system_companies
            # وإخفاء صلاحيات django admin الأساسية
            form.base_fields['permissions'].queryset = Permission.objects.filter(
                Q(content_type__app_label='system_companies') |
                Q(content_type__app_label__in=['auth', 'admin', 'contenttypes', 'sessions'])
            )
        return form

    def get_queryset(self, request):
        # إذا كنت تريد أيضاً تصفية المجموعات المعروضة
        return super().get_queryset(request)

# إلغاء تسجيل النموذج الأصلي وإعادة تسجيله مع التخصيص
admin.site.unregister(Group)
admin.site.register(Group, CompanyGroupAdmin)

# -------------------------------
User = get_user_model()

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_phone', 'get_profile_picture', 'is_staff')
    list_select_related = ('company_profile', )  # ✅ هنا بدلنا profile إلى company_profile

    def get_phone(self, instance):
        return instance.company_profile.phone_number if hasattr(instance, 'company_profile') else ''
    get_phone.short_description = 'رقم الهاتف'

    def get_profile_picture(self, instance):
        if hasattr(instance, 'company_profile') and instance.company_profile.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', instance.company_profile.profile_picture.url)
        return "لا توجد صورة"
    get_profile_picture.short_description = 'صورة الملف الشخصي'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# -----------------------------------------
@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ("date", "check_in_time", "check_out_time", "status_badge", "shift_type", 'notes')
    list_filter = ("status",)
    search_fields = ("date", "check_in_time")
# انواع الشاحنات --------------------------------
@admin.register(TrucksTypes)
class TrucksTypesAdmin(BaseAdmin):
    list_display = ("manufacturer", "description", "dimensions", "status_badge", "progress_bar", 'action_buttons')
    list_filter = ("status",)
    search_fields = ("manufacturer", "description")
    field = (('manufacturer', 'description'), ('dimensions', 'status_badge'), ('progress_bar'))


    # --------------------------------------------------------------
# احتفظ بنسخة من الدالة الأصلية للصفحة الرئيسية
original_index = admin.site.index

def custom_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}

    today = timezone.now().date()
    extra_context['entry_count'] = Entry_and_exit.objects.filter(entry_date__date=today).count()
    extra_context['exit_count'] = Entry_and_exit.objects.filter(exit_date__date=today).count()
    extra_context['violationrecord_count'] =  ViolationRecord.objects.count()
    extra_context['trucks_count'] = Trucks.objects.count()


    # جلب آخر 5 سجلات (مثلاً) من جدول WeightCard
    latest_cards = WeightCard.objects.order_by('-id')[:5]
    extra_context['latest_cards'] = latest_cards

    return original_index(request, extra_context)

admin.site.index = custom_index
admin.site.index_template = "admin/custom_index.html"
# -----------------------------------------------------------
#  ----------------------- السائقيين----------------------------
@admin.register(DriverNeme)
class DriverNemeAdmin(BaseAdmin):
    list_display = ['driver_name', 'phone_number', 'address', 'card_number', 'date_of_registration', 'number_of_trucks', 'action_buttons']
    search_fields = ['driver_name']
    date_hierarchy = 'date_of_registration'
    

# -----------------------------------------------------------
#  ----------------------- الشاحنات ----------------------------
@admin.register(Trucks)
class TrucksAdmin(BaseAdmin):
    list_display = ['plate_number', 'truck_type', 'formatted_registration_date', 'condition', 'driver_name', 'action_buttons']
    search_fields = ['plate_number']
    # list_filter = (('registration_date', DateRangeFilter),)  # هنا تضيف فلتر النطاق
    date_hierarchy = 'registration_date'
    # list_filter = ("condition",)

    def formatted_registration_date(self, obj):
        return localtime(obj.registration_date).strftime('%Y-%m-%d %H:%M')
    formatted_registration_date.short_description = 'تاريخ التسجيل'


# -----------------------------------------------------------
#  ----------------------- عمليات الدخول والخروج ----------------------------
class Entry_and_exitAdmin(BaseAdmin):
    list_display = ('plate_number_E_e', 'entry_image_tag', 'exit_image_tag', 'entry_date', 'exit_date', 'action_buttons')  # Display images as columns
    # readonly_fields = ('entry_image_tag', 'exit_image_tag')  # Prevent modifying images in the admin panel
    
    

admin.site.register(Entry_and_exit, Entry_and_exitAdmin)
# -----------------------------------------------------------
#  ----------------------- الوزن القانوني ----------------------------
@admin.register(Legal_weight)
class Legal_weightAdmin(BaseAdmin):
    list_display = ['manufacturer_L_W', 'legal_weight_L_W', 'number_of_axes', 'registration_date', 'action_buttons']
    search_fields = ['manufacturer_L_W']
    date_hierarchy = 'registration_date'
    

# -----------------------------------------------------------
#  ----------------------- بطاقات الوزن  ----------------------------
class WeightCardAdmin(BaseAdmin):
    list_display = ("id","plate_number", "empty_weight", "loaded_weight", "net_weight", "entry_date", "exit_date","quantity", "status_complet", 'action_buttons')
    readonly_fields = ("net_weight",)  # منع تعديل الوزن الصافي يدويًا
    list_filter = ('status',)
    
    search_fields = ('plate_number__plate_number',) 


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['entry_date', 'exit_date']:
            return None  # إخفاء الحقول من الفورم
        return super().formfield_for_dbfield(db_field, **kwargs)

    fieldsets = (
        (" مسجل بيانات الوزن", {
            "fields": (('empty_weight','loaded_weight'), "net_weight"),
            "classes": ("weight-section",),
        }),
        (" بطاقة الوزن", {
            "fields": ("plate_number","driver_name","quantity","material"),
            "classes": ("card-section",),
        }),
    )
admin.site.register(WeightCard, WeightCardAdmin)

# -----------------------------------------------------------
# -------------------------دالة الفاتوره----------------------------------
@admin.register(Invoice)
class InvoiceAdmin(BaseAdmin):
    list_display = ['id', 'weight_card', 'material', 'quantity', 'datetime', 'net_weight', 'print_invoice_button', 'action_buttons']
    readonly_fields = ('weight_card', 'net_weight', 'print_invoice_button')

    

    def has_add_permission(self, request):
        """
        منع إنشاء فاتورة جديدة إلا إذا كانت هناك بطاقة وزن على الأقل.
        """
        return WeightCard.objects.exists()  # ✅ يسمح بإنشاء فاتورة فقط إذا كان هناك بطاقة وزن

    def save_model(self, request, obj, form, change):
        """
        منع إنشاء فاتورة جديدة بدون بطاقة وزن، ولكن السماح بتعديل فاتورة موجودة.
        """
        if not change and not obj.weight_card:
            messages.error(request, "لا يمكن إنشاء فاتورة بدون بطاقة وزن.")
            raise ValidationError("يجب إنشاء بطاقة وزن قبل الفاتورة.")

        super().save_model(request, obj, form, change)

    def get_urls(self):
        """إضافة رابط مخصص لطباعة الفاتورة في لوحة الإدارة."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:invoice_id>/print/',
                self.admin_site.admin_view(self.print_invoice_view),
                name='invoice-print',
            ),
        ]
        return custom_urls + urls

    def print_invoice_view(self, request, invoice_id):
        """
        هذه الدالة تعرض صفحة HTML يمكن طباعتها.
        يمكنك تصميم القالب بالشكل الذي تريده.
        """
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        
        context = {
            'invoice': invoice,
            # يمكنك تمرير أي بيانات أخرى تحتاجها للقالب
        }
        # نفترض أن لدينا قالب باسم admin/print_invoice.html
        return render(request, 'admin/print_invoice.html' ,context)

    def print_invoice_button(self, obj):
        """
        دالة بسيطة تعيد رابط (زر) للطباعة في صفحة تفاصيل الفاتورة.
        سيظهر هذا الزر في حقل مخصص (ضمن list_display أو ضمن read_only_fields).
        """
        url = reverse('admin:invoice-print', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">طباعة الفاتورة</a>', url)

    print_invoice_button.short_description = "طباعة"
    

# -----------------------------------------------------------
#  ----------------------- المواد ----------------------------
@admin.register(Material)
class MaterialAdmin(BaseAdmin):
    list_display = ['id', 'name_material', 'description', 'unit', 'date_and_time', 'action_buttons']

    

# -----------------------------------------------------------
#  ----------------------- المخالفات  ----------------------------
@admin.register(ViolationRecord)
class ViolationRecordAdmin(BaseAdmin):
    list_display = ['plate_number_vio', 'violation_type', 'timestamp', 'device_vio','entry_exit_log','weight_card_vio','image_violation']
    search_fields = ['plate_number_vio']
    date_hierarchy = 'timestamp'
    # fields = (('plate_number_vio' , 'violation_type' ))
# -----------------------------------------------------------
#  ----------------------- اعدادات الاجهزه ----------------------------
@admin.register(Devices)
class DevicesAdmin(BaseAdmin):
    list_display = ['name_devices', 'address_ip', 'connection_type', 'device_status','location', 'action_buttons']
    search_fields = ['name_devices']
    date_hierarchy = 'last_date_settings_updated'
    exclude = ('username', 'password')  # إخفاء الحقول من نموذج الإدخال العادي

    class Media:
        js = ('https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',  # تحميل jQuery
              'https://cdn.jsdelivr.net/npm/sweetalert2@11',  # تحميل SweetAlert2
              'js/custom_admin.js') 


    def save_model(self, request, obj, form, change):
        if not obj.check_camera_connection():
            messages.error(request, f"❌ لا يمكن حفظ الجهاز! لم يتم العثور على الكاميرا عبر {obj.connection_type}.")
            return  
        
        super().save_model(request, obj, form, change)
        messages.success(request, f"✅ تم الاتصال بنجاح بالكاميرا عبر {obj.connection_type} ({obj.address_ip or obj.port_number}).")

