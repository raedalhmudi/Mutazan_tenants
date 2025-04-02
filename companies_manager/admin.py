from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission # استيراد النماذج المدمجة
from .models import *  # استيراد باقي النماذج مثل Tenant و Domain
from django.utils.html import format_html
from django.utils.html import mark_safe
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

class CompanyGroupAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'permissions' in form.base_fields:
            # فلترة الصلاحيات لتبقي فقط تلك الخاصة بتطبيق system_companies
            # وإخفاء صلاحيات django admin الأساسية
            form.base_fields['permissions'].queryset = Permission.objects.filter(
                Q(content_type__app_label='companies_manager') |
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
    fields = ('profile_picture', 'phone_number', 'address')

class CustomUserAdmin(UserAdmin):
    def add_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super().add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super().change_view(*args, **kwargs)

    list_display = ('username', 'email', 'get_phone')
    
    def get_phone(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else ''
    get_phone.short_description = 'رقم الهاتف'

# إلغاء التسجيل القديم وإعادة التسجيل
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class TenantAdminSete(admin.AdminSite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تسجيل النماذج الخاصة بالمستأجرين
        self.register(Company)
        # def get_queryset(self, request):
        #     queryset = super().get_queryset(request)
        #     return queryset.filter(domain=request.get_host())
        self.register(ViolationsType)
        self.register(Domain)

        # تسجيل نماذج المستخدمين والمجموعات
        self.register(User)  # جدول المستخدمين
        self.register(Group)  # جدول المجموعات

# إنشاء كائن من لوحة الإدارة المخصصة
tenant_admin_site = TenantAdminSete(name="tenant_admin_site")
