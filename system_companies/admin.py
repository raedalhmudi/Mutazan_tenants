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
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from companies_manager.models import UserProfile
from django.contrib.auth.models import Group, Permission
from django.utils.timezone import localtime
# from rangefilter.filters import DateRangeFilter
from django.db.models import Q
from django.db import models
from django_tenants.utils import get_tenant, get_tenant_model

class CustomAdminSite(admin.AdminSite):
    """تخصيص عنوان لوحة الإدارة لكل مستأجر"""
    
    def get_site_header(self, request):
        tenant = get_tenant(request)
        if isinstance(tenant, get_tenant_model()):
            return tenant.company_name  # استخدام اسم المستأجر
        return "إدارة النظام"

    def each_context(self, request):
        context = super().each_context(request)
        context['site_header'] = self.get_site_header(request)
        context['site_title'] = self.get_site_header(request)
        return context

# استبدال `admin.site` بالنسخة المخصصة
custom_admin = CustomAdminSite(name='custom_admin')

# استبدال `admin.site` بالإدارة الجديدة بدون إعادة تسجيل النماذج
admin.site.__class__ = CustomAdminSite

# -----------------------------------------
class BaseAdmin(admin.ModelAdmin):
    """فلترة أي ForeignKey يشير إلى جدول يحتوي على الحقل condition=True فقط."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """فلترة العلاقات الخارجية (ForeignKey) بناءً على وجود حقل condition في النموذج المرتبط."""
        related_model = db_field.related_model  # جلب الموديل المرتبط بـ FK
        
        # التأكد من أن الجدول يحتوي على الحقل 'condition' ثم تطبيق الفلترة
        if related_model and hasattr(related_model, 'condition'):
            kwargs["queryset"] = related_model.objects.filter(condition=True)  # جلب العناصر المتاحة فقط
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
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
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_phone', 'get_profile_picture', 'is_staff')
    list_select_related = ('profile', )
    
    def get_phone(self, instance):
        return instance.profile.phone_number if hasattr(instance, 'profile') else ''
    get_phone.short_description = 'رقم الهاتف'

    def get_profile_picture(self, instance):
        """عرض صورة المستخدم في الـ Admin"""
        if hasattr(instance, 'profile') and instance.profile.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', instance.profile.profile_picture.url)
        return "لا توجد صورة"
    get_profile_picture.short_description = 'صورة الملف الشخصي'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
# -----------------------------------------
@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ("date", "check_in_time", "check_out_time", "status", "shift_type", 'notes')
    list_filter = ("status",)
    search_fields = ("date", "check_in_time")
# انواع الشاحنات --------------------------------
@admin.register(TrucksTypes)
class TrucksTypesAdmin(BaseAdmin):
    list_display = ("manufacturer", "description", "dimensions", "status_badge", "progress_bar", 'action_buttons')
    list_filter = ("status",)
    search_fields = ("manufacturer", "description")
    field = (('manufacturer', 'description'),('dimensions', 'status_badge'),('progress_bar'))
    
    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_truckstypes_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_truckstypes_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

    def status_badge(self, obj):
        """عرض الحالة كشارة (Badge) في Django Admin"""
        color = "green" if obj.status else "red"
        status_text = "متاح" if obj.status else "غير متاح"
        return format_html(
            f'<span style="color:white; background-color:{color}; padding:4px 8px; border-radius:5px;">{status_text}</span>'
        )
    
    status_badge.short_description = "الحالة"

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
    # --------------------------------------------------------------
# احتفظ بنسخة من الدالة الأصلية للصفحة الرئيسية
original_index = admin.site.index

def custom_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}

    today = timezone.now().date()
    extra_context['entry_count'] = Entry_and_exit.objects.filter(entry_date__date=today).count()
    extra_context['exit_count'] = Entry_and_exit.objects.filter(exit_date__date=today).count()
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
    
    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_driverneme_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_driverneme_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML
# -----------------------------------------------------------
#  ----------------------- الشاحنات ----------------------------
@admin.register(Trucks)
class TrucksAdmin(BaseAdmin):
    list_display = ['plate_number', 'truck_type', 'formatted_registration_date', 'condition', 'driver_name', 'action_buttons']
    search_fields = ['plate_number']
    # list_filter = (('registration_date', DateRangeFilter),)  # هنا تضيف فلتر النطاق
    date_hierarchy = 'registration_date'

    def formatted_registration_date(self, obj):
        return localtime(obj.registration_date).strftime('%Y-%m-%d %H:%M')
    formatted_registration_date.short_description = 'تاريخ التسجيل'

    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_trucks_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_trucks_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML
# -----------------------------------------------------------
#  ----------------------- عمليات الدخول والخروج ----------------------------
class Entry_and_exitAdmin(BaseAdmin):
    list_display = ('plate_number_E_e', 'entry_image_tag', 'exit_image_tag', 'entry_date', 'exit_date', 'action_buttons')  # Display images as columns
    readonly_fields = ('entry_image_tag', 'exit_image_tag')  # Prevent modifying images in the admin panel
    
    # def formatted_entry_date(self, obj):
    #     return localtime(obj.entry_date).strftime('%Y-%m-%d %H:%M')
    # formatted_entry_date.short_description = 'تاريخ '

    # def formatted_exit_date(self, obj):
    #     return localtime(obj.exit_date).strftime('%Y-%m-%d %H:%M')
    # formatted_exit_date.short_description = 'تاريخ '

    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_entry_and_exit_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_entry_and_exit_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

admin.site.register(Entry_and_exit, Entry_and_exitAdmin)
# -----------------------------------------------------------
#  ----------------------- الوزن القانوني ----------------------------
@admin.register(Legal_weight)
class Legal_weightAdmin(BaseAdmin):
    list_display = ['manufacturer_L_W', 'legal_weight_L_W', 'number_of_axes', 'registration_date', 'action_buttons']
    search_fields = ['manufacturer_L_W']
    date_hierarchy = 'registration_date'
    
    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_legal_weight_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_legal_weight_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

# -----------------------------------------------------------
#  ----------------------- بطاقات الوزن  ----------------------------
class WeightCardAdmin(BaseAdmin):
    list_display = ("plate_number", "empty_weight", "loaded_weight", "net_weight", "entry_date", "exit_date","quantity", "status", 'action_buttons')
    readonly_fields = ("net_weight",)  # منع تعديل الوزن الصافي يدويًا
    list_filter = ('status',)
    
    search_fields = ('plate_number__plate_number',) 


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['entry_date', 'exit_date']:
            return None  # إخفاء الحقول من الفورم
        return super().formfield_for_dbfield(db_field, **kwargs)


    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_weightcard_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_weightcard_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

    fieldsets = (
        ("📌 مسجل بيانات الوزن", {
            "fields": (('empty_weight','loaded_weight'), "net_weight"),
            "classes": ("weight-section",),
        }),
        ("📜 بطاقة الوزن", {
            "fields": ("plate_number","driver_name","quantity","material"),
            "classes": ("card-section",),
        }),
    )
admin.site.register(WeightCard, WeightCardAdmin)

# -----------------------------------------------------------
# -------------------------دالة الفاتوره----------------------------------
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'weight_card', 'material', 'quantity', 'datetime', 'net_weight', 'print_invoice_button', 'action_buttons']
    readonly_fields = ('weight_card', 'net_weight', 'print_invoice_button')

    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_invoice_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_invoice_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML


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
    # ---------------------------------------------------------------------
    
    # Add custom logic here for fields like weight_card and user if needed
    
    # Optionally, you can define methods to show more details of related fields
    # def user_name(self, obj):
    #     return obj.user.username if obj.user else 'No User'
    # user_name.short_description = 'User Name'
    # list_display.append('user_name')
    

# -----------------------------------------------------------
#  ----------------------- المواد ----------------------------
@admin.register(Material)
class MaterialAdmin(BaseAdmin):
    list_display = ['id', 'name_material', 'description', 'unit', 'date_and_time', 'action_buttons']

    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_material_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_material_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

# -----------------------------------------------------------
#  ----------------------- المخالفات  ----------------------------
@admin.register(ViolationRecord)
class ViolationRecordAdmin(BaseAdmin):
    list_display = ['plate_number_vio', 'violation_type', 'timestamp', 'device_vio','entry_exit_log','weight_card_vio','image_violation']
    search_fields = ['plate_number_vio']
    date_hierarchy = 'timestamp'
    # fields = (('plate_number_vio' , 'violation_type' ))

    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_violationrecord_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_violationrecord_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

# # -----------------------------------------------------------
# # -------------اختبار الاتصال---------------------------------
# @admin.register(Connection)
# class ConnectionAdmin(admin.ModelAdmin):
#     list_display = ('connection_name', 'date_and_tim', 'check_connection_button', 'action_buttons')
#     search_fields = ['connection_name']
#     date_hierarchy = 'date_and_tim'
    
#     def action_buttons(self, obj):
#         # رابط التعديل
#         edit_url = reverse('admin:system_companies_connection_change', args=[obj.id])
#         # رابط الحذف
#         delete_url = reverse('admin:system_companies_connection_delete', args=[obj.id])
        
#         return format_html(
#             '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
#             '<i class="fas fa-edit"></i> Edit</a>'
#             '<a href="{}" class="btn btn-danger btn-sm">'
#             '<i class="fas fa-trash"></i> Delete</a>',
#             edit_url, delete_url
#         )
#     action_buttons.short_description = 'الإجراءات'  # عنوان العمود
#     action_buttons.allow_tags = True  # السماح بعرض HTML

#     def check_connection_button(self, obj):
#         return format_html(
#             '<a class="button" href="{}">اختبار الاتصال</a>',
#             f"/admin/company_app/connection/{obj.id}/check/"
#         )

#     check_connection_button.short_description = "اختبار الاتصال"
#     check_connection_button.allow_tags = True

#     def get_urls(self):
#         from django.urls import path
#         urls = super().get_urls()
#         custom_urls = [
#             path(
#                 '<path:object_id>/check/',
#                 self.admin_site.admin_view(self.check_connection),
#                 name='check-connection',
#             ),
#         ]
#         return custom_urls + urls

#     def check_connection(self, request, object_id):
#         connection = Connection.objects.get(id=object_id)

#         # هنا نقوم بمحاكاة التحقق الفعلي من الجهاز المتصل
#         device_connected = self.is_device_connected(connection.connection_name)

#         if device_connected:
#             self.message_user(request, f"✅ {connection.connection_name}: الاتصال ناجح والجهاز متصل.", messages.SUCCESS)
#         else:
#             self.message_user(request, f"❌ {connection.connection_name}: الاتصال غير ناجح، لا يوجد جهاز متصل!", messages.ERROR)

#         return redirect('/admin/company_app/connection/')

#     def is_device_connected(self, connection_type):
#         """
#         دالة محاكاة للتحقق مما إذا كان هناك جهاز متصل فعليًا أم لا.
#         يمكن استبدال هذا الجزء بفحص فعلي للأجهزة حسب نوع الاتصال.
#         """
#         import random

#         # محاكاة الاتصال الفعلي بالجهاز (هنا نجعل بعض الاتصالات ناجحة وأخرى فاشلة)
#         fake_device_status = {
#             'USB': random.choice([True, False]),  # أحيانًا متصل وأحيانًا غير متصل
#             'WiFi': True,  # نفترض أن الاتصال اللاسلكي دائمًا ناجح
#             'Serial': random.choice([True, False]),  # عشوائيًا ناجح أو فاشل
#             'API': True  # نفترض أن API متاحة دائمًا
#         }

#         return fake_device_status.get(connection_type, False)  # القيمة الافتراضية هي False إذا كان النوع غير موجود
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

    def action_buttons(self, obj):
        # رابط التعديل
        edit_url = reverse('admin:system_companies_devices_change', args=[obj.id])
        # رابط الحذف
        delete_url = reverse('admin:system_companies_devices_delete', args=[obj.id])
        
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm" style="margin-right: 5px;">'
            '<i class="fas fa-edit"></i> Edit</a>'
            '<a href="{}" class="btn btn-danger btn-sm">'
            '<i class="fas fa-trash"></i> Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'الإجراءات'  # عنوان العمود
    action_buttons.allow_tags = True  # السماح بعرض HTML

    def save_model(self, request, obj, form, change):
        if not obj.check_camera_connection():
            messages.error(request, f"❌ لا يمكن حفظ الجهاز! لم يتم العثور على الكاميرا عبر {obj.connection_type}.")
            return  
        
        super().save_model(request, obj, form, change)
        messages.success(request, f"✅ تم الاتصال بنجاح بالكاميرا عبر {obj.connection_type} ({obj.address_ip or obj.port_number}).")

# admin.site.register(Devices, DevicesAdmin)
# ----------------------------------------------------------------------------------------------------
# --------------------------------المستخدمين-----------------------------------------------------
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     # الحقول التي تظهر عند عرض المستخدم
#     def image_tag(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="70" height="70" style="border-radius: 70%;" />', obj.image.url)
#         return "لا توجد صورة"

#     image_tag.short_description = "الصورة"
#     # الحقول التي تظهر عند عرض المستخدم
#     fieldsets = UserAdmin.fieldsets + (
#         ("معلومات إضافية", {'fields': ('address', 'phone_number', 'image')}),
#     )

#     # الحقول التي تظهر عند إنشاء مستخدم جديد
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         ("معلومات إضافية", {'fields': ('address', 'phone_number', 'image')}),
#     )

#     # الحقول المعروضة في قائمة المستخدمين
#     list_display = ('username', 'email', 'phone_number', 'address', 'is_staff', 'is_active', 'image_tag')

#     # الحقول التي يمكن البحث بها
#     search_fields = ('username', 'email', 'phone_number')

#     # الحقول التي يمكن تعديلها مباشرة من قائمة المستخدمين
#     list_editable = ('phone_number', 'address')

# # تسجيل الموديل مع لوحة التحكم
# # admin.site.register(CustomUser, CustomUserAdmin)




# # ----------------------------------------------------------------------------------------------------
# # ----------------------------------------------------الدوام-------------------------
# @admin.register(Attendance)
# class AttendanceAdmin(admin.ModelAdmin):
#     list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 'total_hours', 'status', 'shift_type')
#     list_filter = ('status', 'shift_type', 'date')  # إضافة فلاتر حسب الحالة ونوع الدوام والتاريخ
#     search_fields = ('employee__name', 'date')  # البحث عن الحضور بالاسم والتاريخ
#     ordering = ('-date',)  # ترتيب السجلات بحيث الأحدث يظهر أولًا
#     readonly_fields = ('total_hours',)  # جعل عدد ساعات العمل للقراءة فقط
#     fieldsets = (
#         ('الموظف والتاريخ', {
#             'fields': ('employee', 'date', 'shift_type')
#         }),
#         ('تفاصيل الحضور', {
#             'fields': ('check_in_time', 'check_out_time', 'total_hours', 'status')
#         }),
#         ('ملاحظات إضافية', {
#             'fields': ('notes',)
#         }),
#     )


# # ----------------------------------------------------------------------------------------------------
# # ----------------------------------------------------------------------------------------------------

