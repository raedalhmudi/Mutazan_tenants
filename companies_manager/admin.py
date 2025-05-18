from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission # استيراد النماذج المدمجة
from .models import *  # استيراد باقي النماذج مثل Tenant و Domain
from django.utils.html import format_html
from django.utils.html import mark_safe
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
# from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from .forms import CompanyAdminForm
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse

# -----------------------------------------
class BaseAdmin(admin.ModelAdmin):
    list_per_page = 6  # عدد الصفوف في كل صفحة
    list_max_show_all = 100  # الحد الأقصى لعرض كل الصفوف في صفحة واحدة
    # paginator = Paginator  # يمكنك تخصيص Paginator إذا أردت
    

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
        if obj.company_condition:
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
    
    status_badge.short_description = "الحالة"
    
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
# -----------------------------------------
# ✅ واجهة الإدارة الرئيسية للمستأجرين
class TenantAdminSite(AdminSite):
    site_header = _("نظام إدارة الشركات")
    index_template = 'companies/custom_public_index.html'

    def index(self, request, extra_context=None):
        UserModel = get_user_model()
        companies = Company.objects.all()
        enriched_companies = []
        
        # متغيرات لحساب المجاميع الكلية
        total_trucks = 0
        total_violations = 0
        total_weight_cards = 0
        total_invoices = 0
        total_devices = 0

        for company in companies:
            try:
                with schema_context(company.schema_name):
                    from system_companies.models import Trucks, ViolationRecord, WeightCard, Invoice, Devices
                    truck_count = Trucks.objects.count()
                    violations_count = ViolationRecord.objects.count()
                    weiht_card_count = WeightCard.objects.count()
                    Invoice_count = Invoice.objects.count()
                    devices_count = Devices.objects.count()
                    
                    # إضافة إلى المجاميع الكلية
                    total_trucks += truck_count
                    total_violations += violations_count
                    total_weight_cards += weiht_card_count
                    total_invoices += Invoice_count
                    total_devices += devices_count
                    
            except Exception as e:
                print(f"⚠️ خطأ في جلب بيانات {company.company_name}: {e}")
                truck_count = 0
                violations_count = 0
                weiht_card_count = 0
                Invoice_count = 0
                devices_count = 0

            enriched_companies.append({
                'company_name': company.company_name,
                'logo': company.logo,
                'trucks': truck_count,
                'violations': violations_count,
                'weiht_card': weiht_card_count,
                'Invoice': Invoice_count,
                'devices': devices_count,
            })

        context = {
            **self.each_context(request),
            'company_count': Company.objects.count(),
            'user_count': UserModel.objects.count(),
            'companies': enriched_companies,
            'total_trucks': total_trucks,  # إجمالي الشاحنات
            'total_violations': total_violations,  # إجمالي المخالفات
            'total_weight_cards': total_weight_cards,  # إجمالي بطاقات الوزن
            'total_invoices': total_invoices,  # إجمالي الفواتير
            'total_devices': total_devices,  # إجمالي الأجهزة
            **(extra_context or {})
        }

        return TemplateResponse(request, self.index_template, context)

tenant_admin_site = TenantAdminSite(name="tenant_admin_site")

# ✅ تخصيص مجموعة المستخدمين
class CompanyGroupAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'permissions' in form.base_fields:
            form.base_fields['permissions'].queryset = Permission.objects.filter(
                Q(content_type__app_label='companies_manager') |
                Q(content_type__app_label__in=['auth', 'admin', 'contenttypes', 'sessions'])
            )
        return form


# admin.py



User = get_user_model()

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_phone', 'get_profile_picture', 'is_staff')
    list_select_related = ('public_profile', )  # ✅ هنا بدلنا profile إلى public_profile

    def get_phone(self, instance):
        return instance.public_profile.phone_number if hasattr(instance, 'public_profile') else ''
    get_phone.short_description = 'رقم الهاتف'

    def get_profile_picture(self, instance):
        if hasattr(instance, 'public_profile') and instance.public_profile.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', instance.public_profile.profile_picture.url)
        return "لا توجد صورة"
    get_profile_picture.short_description = 'صورة الملف الشخصي'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



# ✅ إدارة الشركات
class CompanyAdmin(BaseAdmin):
    form = CompanyAdminForm
    list_display = ("company_name", "registration_number", "country", "phone_number", "email","status_badge", "founded_date", "admin_user", 'action_buttons')
    search_fields = ("company_name", "registration_number", "country", "email")
    list_filter = ("country", "founded_date", "company_condition")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {
            "fields": ("company_name", "business_type", "registration_number", "country", "address", "phone_number", "email", "company_condition")
        }),
        ("معلومات إضافية", {
            "fields": ( "logo", "employees_count", "founded_date", "services_offered", "port_license_number", "admin_user"),
        }),
    )



    class Media:
        css = {
            'all': ('common/css/custom_admin.css',)  # تأكد أن المسار هذا صحيح داخل مجلد static
        }

# ✅ إدارة المخالفات
class ViolationsTypeAdmin(BaseAdmin):
    list_display = ("name", "penalty_amount", "violation_code", "created_at", "updated_at")
    search_fields = ("name", "violation_code")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "description", "penalty_amount", "violation_code")}),
        ("تواريخ", {"fields": ("created_at", "updated_at")}),
    )


class ComActivityLogAdmin(BaseAdmin):
    list_display = ('id','user_image','user','comactivity', 'action', 'timestamp', 'ip_address', 'module','action_buttons')
    search_fields = ('action', 'user__username')
    list_filter = ('module', 'timestamp')

    def user_image(self, obj):
        if obj.user and hasattr(obj.user, 'public_profile') and obj.user.public_profile.profile_picture:
            return format_html('<img src="{}" style="width:40px; height:40px; border-radius:50%;" />',
                            obj.user.public_profile.profile_picture.url)
        return "—"
    user_image.short_description = 'الصورة'

# -----------------------------------------

# ✅ إدارة الدومينات
class DomainAdmin(BaseAdmin):
    list_display = ("domain", "tenant","action_buttons")
    search_fields = ("domain", "tenant__company_name")


# -----------------------------------------
class Legal_weightAdmin(BaseAdmin):
    list_display = [ 'legal_weight_L_W', 'number_of_axes', 'registration_date',"action_buttons"]
    # search_fields = ['manufacturer_L_W']
    date_hierarchy = 'registration_date'
    

    

# ✅ التسجيل في tenant_admin_site فقط
tenant_admin_site.register(User, CustomUserAdmin)
tenant_admin_site.register(Group, CompanyGroupAdmin)
tenant_admin_site.register(Company, CompanyAdmin)
tenant_admin_site.register(ViolationsType, ViolationsTypeAdmin)
tenant_admin_site.register(ComActivityLog, ComActivityLogAdmin)
tenant_admin_site.register(Domain, DomainAdmin)
tenant_admin_site.register(Legal_weight, Legal_weightAdmin)
























from django.contrib import admin
# from django.contrib.auth.models import User, Group, Permission # استيراد النماذج المدمجة
# from .models import *  # استيراد باقي النماذج مثل Tenant و Domain
# from django.utils.html import format_html
# from django.utils.html import mark_safe
# from django.urls import reverse
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
# from .models import UserProfile
# from .forms import CustomUserCreationForm
# from django.contrib.auth.models import Group, Permission
# from django.contrib.auth import get_user_model
# from django.db.models import Q
# from django.utils.translation import gettext_lazy as _
# from django.contrib.admin import AdminSite
# from django.template.response import TemplateResponse


# class TenantAdminSete(admin.AdminSite):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # تسجيل النماذج الخاصة بالمستأجرين
#         self.register(Company)
#         # def get_queryset(self, request):
#         #     queryset = super().get_queryset(request)
#         #     return queryset.filter(domain=request.get_host())
#         self.register(ViolationsType)
#         self.register(Domain)

#         # تسجيل نماذج المستخدمين والمجموعات
#         self.register(User)  # جدول المستخدمين
#         self.register(Group)  # جدول المجموعات

# # إنشاء كائن من لوحة الإدارة المخصصة
# tenant_admin_site = TenantAdminSete(name="tenant_admin_site")


# class CompanyGroupAdmin(admin.ModelAdmin):
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if 'permissions' in form.base_fields:
#             # فلترة الصلاحيات لتبقي فقط تلك الخاصة بتطبيق system_companies
#             # وإخفاء صلاحيات django admin الأساسية
#             form.base_fields['permissions'].queryset = Permission.objects.filter(
#                 Q(content_type__app_label='companies_manager') |
#                 Q(content_type__app_label__in=['auth', 'admin', 'contenttypes', 'sessions'])
#             )
#         return form

#     def get_queryset(self, request):
#         # إذا كنت تريد أيضاً تصفية المجموعات المعروضة
#         return super().get_queryset(request)

# # إلغاء تسجيل النموذج الأصلي وإعادة تسجيله مع التخصيص
# tenant_admin_site.unregister(Group)
# tenant_admin_site.register(Group, CompanyGroupAdmin)


# # -------------------------------

# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'الملف الشخصي'
#     fk_name = 'user'
#     fields = ('phone_number', 'address', 'profile_picture')


# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     inlines = [UserProfileInline]

#     # حدد الحقول في صفحة إضافة المستخدم
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'password1', 'password2', 'phone_number', 'address', 'profile_picture'),
#         }),
#     )

#     # حدد الحقول في صفحة تعديل المستخدم
#     fieldsets = (
#         (None, {
#             'fields': ('username', 'email', 'password'),
#         }),
#         ('Personal info', {
#             'fields': ('first_name', 'last_name', 'phone_number', 'address', 'profile_picture'),
#         }),
#         ('Permissions', {
#             'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
#         }),
#         ('Important dates', {
#             'fields': ('last_login', 'date_joined'),
#         }),
#     )


#     def save_model(self, request, obj, form, change):
#         """يتم هنا حفظ UserProfile تلقائيًا عند إضافة مستخدم جديد"""
#         super().save_model(request, obj, form, change)
#         if not change:  # يعني مستخدم جديد
#             UserProfile.objects.update_or_create(
#                 user=obj,
#                 defaults={
#                     'phone_number': form.cleaned_data.get('phone_number'),
#                     'address': form.cleaned_data.get('address'),
#                     'profile_picture': form.cleaned_data.get('profile_picture')
#                 }
#             )

# tenant_admin_site.unregister(User)
# tenant_admin_site.register(User, CustomUserAdmin)




# # ---------------------------------------------------------------
# # في ملف admin.py

# # نموذج عرض شركة
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ("company_name", "business_type", "registration_number", "country", "phone_number", "email", "founded_date", "admin_user")
#     search_fields = ("company_name", "registration_number", "country", "email")
#     list_filter = ("country", "founded_date")
#     readonly_fields = ("created_at",)
#     fieldsets = (
#         (None, {
#             "fields": ("company_name", "business_type", "registration_number", "country", "address", "phone_number", "email", "logo", "employees_count", "founded_date", "services_offered", "port_license_number", "admin_user")
#         }),
#         ("معلومات إضافية", {
#             "fields": ("created_at",),
#         }),
#     )

# # نموذج عرض نوع المخالفة
# class ViolationsTypeAdmin(admin.ModelAdmin):
#     list_display = ("name", "penalty_amount", "violation_code", "created_at", "updated_at")
#     search_fields = ("name", "violation_code")
#     list_filter = ("created_at", "updated_at")
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (None, {
#             "fields": ("name", "description", "penalty_amount", "violation_code")
#         }),
#         ("تواريخ", {
#             "fields": ("created_at", "updated_at")
#         }),
#     )

# # نموذج عرض دومين
# class DomainAdmin(admin.ModelAdmin):
#     list_display = ("domain", "tenant")
#     search_fields = ("domain", "tenant__company_name")

# # التسجيل في tenant_admin_site بدل admin.site
# tenant_admin_site.register(Company, CompanyAdmin)
# tenant_admin_site.register(ViolationsType, ViolationsTypeAdmin)
# tenant_admin_site.register(Domain, DomainAdmin)

# # ---------------------------------------------------------------


# # استخدم النسخة الأصلية من index
# # companies_manager/admin.py



# class TenantAdminSite(AdminSite):
#     site_header = _("نظام إدارة الشركات")
#     index_template = 'admin/custom_public_index.html'

#     def index(self, request, extra_context=None):
#         User = get_user_model()
#         company_count = Company.objects.count()
#         user_count = User.objects.count()

#         context = {
#             **self.each_context(request),
#             'company_count': company_count,
#             'user_count': user_count,
#             **(extra_context or {})
#         }
#         return TemplateResponse(request, self.index_template, context)



















