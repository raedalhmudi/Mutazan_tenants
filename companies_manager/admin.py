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
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse

# ✅ واجهة الإدارة الرئيسية للمستأجرين
class TenantAdminSite(AdminSite):
    site_header = _("نظام إدارة الشركات")
    index_template = 'companies/custom_public_index.html'

    def index(self, request, extra_context=None):
        UserModel = get_user_model()
        companies = Company.objects.all()
        enriched_companies = []

        for company in companies:
            try:
                with schema_context(company.schema_name):
                    from system_companies.models import Trucks, ViolationRecord, WeightCard, Invoice
                    truck_count = Trucks.objects.count()
                    violations_count = ViolationRecord.objects.count()
                    weiht_card_count = WeightCard.objects.count()
                    Invoice_count = Invoice.objects.count()
            except Exception as e:
                print(f"⚠️ خطأ في جلب بيانات {company.company_name}: {e}")
                truck_count = 0
                violations_count = 0
                weiht_card_count = 0
                Invoice_count = 0

            enriched_companies.append({
                'company_name': company.company_name,
                'logo': company.logo,
                'trucks': truck_count,
                'violations': violations_count,
                'weiht_card': weiht_card_count,
                'Invoice': Invoice_count,
            })

        context = {
            **self.each_context(request),
            'company_count': Company.objects.count(),
            'user_count': UserModel.objects.count(),
            'companies': enriched_companies,  # ← نمررها هنا للقالب
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
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_name", "business_type", "registration_number", "country", "phone_number", "email", "founded_date", "admin_user")
    search_fields = ("company_name", "registration_number", "country", "email")
    list_filter = ("country", "founded_date")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {
            "fields": ("company_name", "business_type", "registration_number", "country", "address", "phone_number", "email")
        }),
        ("معلومات إضافية", {
            "fields": ( "logo", "employees_count", "founded_date", "services_offered", "port_license_number", "admin_user"),
        }),
    )

# ✅ إدارة المخالفات
class ViolationsTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "penalty_amount", "violation_code", "created_at", "updated_at")
    search_fields = ("name", "violation_code")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "description", "penalty_amount", "violation_code")}),
        ("تواريخ", {"fields": ("created_at", "updated_at")}),
    )

# ✅ إدارة الدومينات
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant")
    search_fields = ("domain", "tenant__company_name")


# ✅ التسجيل في tenant_admin_site فقط
tenant_admin_site.register(User, CustomUserAdmin)
tenant_admin_site.register(Group, CompanyGroupAdmin)
tenant_admin_site.register(Company, CompanyAdmin)
tenant_admin_site.register(ViolationsType, ViolationsTypeAdmin)
tenant_admin_site.register(Domain, DomainAdmin)























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



















