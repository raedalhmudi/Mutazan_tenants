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
from .forms import WeightCardForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.utils.timezone import localtime
from django.db.models import Q
from companies_manager.models import Legal_weight
from django.db import models
from django_tenants.utils import get_tenant, get_tenant_model
from .models import UserProfile  # هذا UserProfile تبع الشركة
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ActivityLog
from django.core.paginator import Paginator as DjangoPaginator
# -----------------------------------------
class CustomPaginator(DjangoPaginator):
    def __init__(self, object_list, per_page, orphans=2, allow_empty_first_page=True):
        super().__init__(
            object_list=object_list,
            per_page=per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page
        )

# -----------------------------------------

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 6  # عدد الصفوف ف   ي كل صفحة
    paginator = CustomPaginator 

    class Media:
        css = {
            'all': ('common/css/system_companies/admin_styles.css',)  # تحديد مكان ملف CSS
        }

    """فلترة أي ForeignKey يشير إلى جدول يحتوي على الحقل condition=True فقط."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """فلترة العلاقات الخارجية (ForeignKey) بناءً على وجود حقل condition في النموذج المرتبط."""
        related_model = db_field.related_model
        
        if related_model and hasattr(related_model, 'condition'):
            kwargs["queryset"] = related_model.objects.filter(condition=True)
        
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
        if obj.status == "complete":
            
            status_text = "مكتمل"
            class_name = "status-badge status-completed"
        else:

            status_text = "غير مكتمل "
            class_name = "status-badge status-pending"

        return format_html(
            f'<span class="{class_name}" {class_name}; padding:4px 8px; border-radius:5px;">{status_text}</span>'
        )

    status_complet.short_description = "الحالة"

    def status_pru(self, obj):
        """عرض الحالة كشارة (Badge) في Django Admin بالتنسيق المطلوب"""
        if obj.pruss_status == "complete":
            
            status_text = "مكتمل"
            class_name = "status-badge status-completed"
        else:

            status_text = "غير مكتمل "
            class_name = "status-badge status-pending"

        return format_html(
            f'<span class="{class_name}" {class_name}; padding:4px 8px; border-radius:5px;">{status_text}</span>'
        )

    status_pru.short_description = "الحالة"

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

    def formatted_registration_date(self, obj):
        return localtime(obj.registration_date).strftime('%Y-%m-%d %H:%M')
    formatted_registration_date.short_description = 'تاريخ التسجيل'
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

class CustomUserAdmin(BaseAdmin,UserAdmin):
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
# @admin.register(TrucksTypes)
# class TrucksTypesAdmin(BaseAdmin):
#     list_display = ("manufacturer", "description", "dimensions", "status_badge", "progress_bar", 'action_buttons')
#     list_filter = ("status",)
#     search_fields = ("manufacturer", "description")
#     field = (('manufacturer', 'description'), ('dimensions', 'status_badge'), ('progress_bar'))


    # --------------------------------------------------------------
# احتفظ بنسخة من الدالة الأصلية للصفحة الرئيسية
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime

original_index = admin.site.index

def custom_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}

    # الحصول على التاريخ اليوم
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    # ----------- دخول وخروج شهرية ----------- 
    entry_count = Entry_and_exit.objects.filter(entry_date__date__gte=start_of_month).count()
    exit_count = Entry_and_exit.objects.filter(exit_date__date__gte=start_of_month).count()
    entry_exit_total = entry_count + exit_count
    target_entry_exit = 500  # الهدف الشهري

    entry_exit_percent = round((entry_exit_total / target_entry_exit) * 100, 1) if target_entry_exit else 0
    entry_exit_offset = 370 - (370 * entry_exit_percent / 100)

    extra_context['entry_count'] = entry_count
    extra_context['exit_count'] = exit_count
    extra_context['entry_exit_percent'] = entry_exit_percent
    extra_context['entry_exit_offset'] = entry_exit_offset

    # ----------- مخالفات شهرية ----------- 
    current_month = today.month
    current_year = today.year

    extra_context['violationrecord_count'] = ViolationRecord.objects.filter(
        timestamp__month=current_month, timestamp__year=current_year).count()

    # ----------- الشاحنات ----------- 
    trucks_count = Trucks.objects.count()
    target_trucks = 100  # الهدف الشهري للشاحنات

    trucks_percent = round((trucks_count / target_trucks) * 100, 1) if target_trucks else 0
    stroke_dashoffset_trucks = 370 - (370 * trucks_percent / 100)

    extra_context['trucks_count'] = trucks_count
    extra_context['trucks_percent'] = trucks_percent
    extra_context['stroke_dashoffset_trucks'] = stroke_dashoffset_trucks

    # ----------- بطاقات الوزن لليوم ----------- 
    today_weight_cards = WeightCard.objects.filter(entry_date__date=today)
    
    weightcard_count_today = today_weight_cards.count()
    completed = today_weight_cards.filter(status="complete").count()
    incomplete = today_weight_cards.exclude(status="complete").count()

    total_weight_today = today_weight_cards.aggregate(total=Sum('net_weight')).get('total') or 0

    # حساب النسب المئوية
    weightcard_completion_percent = round((completed / weightcard_count_today) * 100, 1) if weightcard_count_today else 0
    weightcard_incomplete_percent = round((incomplete / weightcard_count_today) * 100, 1) if weightcard_count_today else 0

    # الهدف المطلوب للوزن اليومي
    target_weight = 10000  # تعديل هذا الرقم حسب الهدف المطلوب
    weightcard_weight_percent = round((total_weight_today / target_weight) * 100, 1) if target_weight else 0

    stroke_dasharray_weight = 370
    stroke_dashoffset_weight = stroke_dasharray_weight - (stroke_dasharray_weight * weightcard_weight_percent / 100)

    extra_context['weightcard_count_today'] = weightcard_count_today
    extra_context['completed_weightcards'] = completed
    extra_context['incomplete_weightcards'] = incomplete
    extra_context['total_weight_today'] = total_weight_today
    extra_context['weightcard_completion_percent'] = weightcard_completion_percent
    extra_context['weightcard_incomplete_percent'] = weightcard_incomplete_percent
    extra_context['target_weight'] = target_weight
    extra_context['weightcard_weight_percent'] = weightcard_weight_percent
    extra_context['stroke_dashoffset_weight'] = stroke_dashoffset_weight

    # ----------- أحدث البطاقات ----------- 
    extra_context['latest_cards'] = WeightCard.objects.order_by('-id')[:5]

    # العودة إلى القالب مع البيانات
    return original_index(request, extra_context)

# تغيير إعدادات القالب
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
    list_display = ['plate_number', 'truck_type', 'formatted_registration_date', 'condition', 'driver_name','number_of_axles', 'action_buttons']
    search_fields = ['plate_number']
    # list_filter = (('registration_date', DateRangeFilter),)  # هنا تضيف فلتر النطاق
    date_hierarchy = 'registration_date'
    # list_filter = ("condition",)



    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()  # هذا سينفذ دالة clean() في النموذج
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            messages.error(request, f"خطأ في الحفظ: {e}")


# -----------------------------------------------------------
#  ----------------------- عمليات الدخول والخروج ----------------------------
class Entry_and_exitAdmin(BaseAdmin):
    list_display = ('name','plate_number_E_e', 'entry_image_tag', 'exit_image_tag', 'entry_date', 'exit_date','status_pru', 'action_buttons')  # Display images as columns
    # readonly_fields = ('entry_image_tag', 'exit_image_tag')  # Prevent modifying images in the admin panel
    list_filter = ('pruss_status',)
    
    

admin.site.register(Entry_and_exit, Entry_and_exitAdmin)
# -----------------------------------------------------------
class InvoiceMaterialInline(admin.TabularInline):
    model = InvoiceMaterial
    extra = 0
    verbose_name = "المادة"
    verbose_name_plural = "المواد المرتبطة بالفاتوره "



# -----------------------------------------------------------
# -----------------------------------------------------------
class WeightCardMaterialInline(admin.TabularInline):
    model = WeightCardMaterial
    extra = 0  # عدد الصفوف الفارغة التي تظهر تلقائيًا
    min_num = 0
    verbose_name = "المادة"
    verbose_name_plural = "المواد المرتبطة بالبطاقة"
    can_delete = True

    def get_queryset(self, request):
        # لتفادي استدعاء المادة غير الموجودة عند الاستعلام
        return super().get_queryset(request).select_related('material')

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


# -----------------------------------------------------------
#  ----------------------- بطاقات الوزن  ----------------------------
class WeightCardAdmin(BaseAdmin):
    inlines = [WeightCardMaterialInline]
    list_display = ("plate_number", "empty_weight", "loaded_weight", "net_weight", "entry_date", "exit_date", "status_complet","quantity","material", 'action_buttons')
    readonly_fields = ("net_weight",)  # منع تعديل الوزن الصافي يدويًا
    list_filter = ('status',)
    
    search_fields = ('plate_number__plate_number',) 

    def material(self, instance):
        return ", ".join([str(m.material) for m in instance.materials.all()])
    material.short_description = 'المادة'

    def quantity(self, instance):
        return ", ".join([str(m.quantity) for m in instance.materials.all()])
    quantity.short_description = 'الكمية'


    def material_and_quantity(self, instance):
        materials = instance.weightcardmaterial_set.all()
        return " | ".join([f"{m.material} ({m.quantity})" for m in materials]) if materials else "-"
    material_and_quantity.short_description = 'المواد والكميات'


    # def delete_model(self, request, obj):
    #     # منع الحذف مع عرض رسالة واضحة
    #     messages.error(request, "❌ لا يمكنك حذف بطاقة وزن.")
    #     return

    # def delete_queryset(self, request, queryset):
    #     # منع حذف عدة فواتير
    #     messages.error(request, "❌ لا يمكنك حذف بطاقة وزن.")
    #     return


    
    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return []
    #     return super().get_inline_instances(request, obj)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['entry_date', 'exit_date']:
            return None  # إخفاء الحقول من الفورم
        return super().formfield_for_dbfield(db_field, **kwargs)

    fieldsets = (
        (" مسجل بيانات الوزن", {
            "fields": (('empty_weight','net_weight'), "loaded_weight"),
            "classes": ("weight-section",),
        }),
        (" بطاقة الوزن", {
            "fields": ("plate_number","driver_name"),
            "classes": ("card-section",),
        }),
    )

    def save_model(self, request, obj, form, change):
        # استخدم هذا قبل الحفظ لالتقاط ما إذا تم تجاوز الوزن
        is_violation = False
        legal_weight = None

        if obj.empty_weight and obj.loaded_weight:
            try:
                legal_entry = Legal_weight.objects.get(number_of_axes=obj.plate_number.number_of_axles)
                legal_weight = legal_entry.legal_weight_L_W
                if obj.loaded_weight > legal_weight:
                    is_violation = True
            except Legal_weight.DoesNotExist:
                pass

        # الآن نحفظ الكائن فعلياً
        super().save_model(request, obj, form, change)

        # بعد الحفظ وعند وجود مخالفة، نعرض الرسالة
        if is_violation:
            messages.warning(request, f"✅ تم تسجيل مخالفة: تجاوز الوزن القانوني ({obj.loaded_weight} طن > {legal_weight} طن)")

admin.site.register(WeightCard, WeightCardAdmin)



# -----------------------------------------------------------
# -------------------------دالة الفاتوره----------------------------------
@admin.register(Invoice)
class InvoiceAdmin(BaseAdmin):
    inlines = [InvoiceMaterialInline]
    list_display = ['id', 'weight_card', 'datetime', 'net_weight', 'print_invoice_button', 'action_buttons']
    readonly_fields = ('weight_card', 'net_weight', 'print_invoice_button')


    def has_add_permission(self, request):
        # ✅ السماح بظهور زر الإضافة، لكن منع العملية برسالة واضحة
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            # منع الإضافة مع رسالة واضحة
            messages.error(request, "❌ لا يمكنك إضافة فاتورة.")
            return redirect('admin:system_companies_invoice_changelist')  # غيّر حسب مسار التطبيق لديك
        # إخفاء النموذج نهائيًا
        messages.error(request, "❌ لا يمكنك إضافة فاتورة.")
        return redirect('admin:system_companies_invoice_changelist')

    def delete_model(self, request, obj):
        # منع الحذف مع عرض رسالة واضحة
        messages.error(request, "❌ لا يمكنك حذف فاتورة.")
        return

    def delete_queryset(self, request, queryset):
        # منع حذف عدة فواتير
        messages.error(request, "❌ لا يمكنك حذف الفواتير.")
        return

    

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
    list_display = ['id', 'quantity_mat','name_material', 'description', 'unit', 'date_and_time', 'action_buttons']

    

# -----------------------------------------------------------
#  ----------------------- المخالفات  ----------------------------
# @admin.register(ViolationRecord)
class ViolationRecordAdmin(BaseAdmin):
    list_display = [
        'plate_number_vio', 
        'violation_type', 
        'get_penalty_amount',
        'get_driner_name',
        'timestamp', 
        'device_vio',
        'entry_exit_log',
        'weight_card_vio',
        'image_violation',
        'action_buttons'
    ]
    search_fields = ['plate_number_vio']
    date_hierarchy = 'timestamp'



    def get_penalty_amount(self, obj):
        try:
            weight_card = obj.weight_card_vio
            if weight_card and weight_card.loaded_weight and weight_card.empty_weight:
                net_weight = weight_card.loaded_weight - weight_card.empty_weight
                legal_weight_entry = Legal_weight.objects.get(number_of_axes=weight_card.plate_number.number_of_axles)
                legal_weight = legal_weight_entry.legal_weight_L_W

                if weight_card.loaded_weight > legal_weight:
                    excess_weight = weight_card.loaded_weight - legal_weight  # بالأطنان
                    penalty = excess_weight * obj.violation_type.penalty_amount
                    return f"{penalty:.2f} $"
        except Exception as e:
            return "—"
        return "—"

    get_penalty_amount.short_description = 'قيمة الغرامة المحتسبة'


admin.site.register(ViolationRecord, ViolationRecordAdmin)
# -----------------------------------------------------------
#  ----------------------- اعدادات الاجهزه ----------------------------
@admin.register(Devices)
class DevicesAdmin(BaseAdmin):
    list_display = ['name_devices', 'address_ip', 'connection_type', 'device_status','location', 'action_buttons']
    search_fields = ['name_devices']
    date_hierarchy = 'last_date_settings_updated'
    fieldsets = (
        ("بيانات الجهاز", {
            "fields": ('name_devices','address_ip',('connection_type','device_status'), "location"),
            "classes": ("denices-section",),
        }),
        ("اعدادات الجهاز", {
            "fields": (
                "port_number", "baud_rate", "initialization_data_size",
                "number_of_initialization_bits", "parity_type", "flow_control",
                "number_of_digits_after_decimal_point", "username", "password"
            ),
            "classes": ("section",),
        }),
    )
    readonly_fields = ('username', 'password')  # إخفاء الحقول من نموذج الإدخال العادي

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



# -----------------------------------------



@admin.register(ActivityLog)
class ActivityLogAdmin(BaseAdmin):
    list_display = ('id', 'user_image','user', 'action', 'timestamp', 'ip_address', 'module')
    search_fields = ('action', 'user__username')
    list_filter = ('module', 'timestamp')

    def user_image(self, obj):
        if obj.user and hasattr(obj.user, 'company_profile') and obj.user.company_profile.profile_picture:
            return format_html('<img src="{}" style="width:40px; height:40px; border-radius:50%;" />',
                               obj.user.company_profile.profile_picture.url)
        return "—"
    user_image.short_description = 'الصورة'


# -----------------------------------------