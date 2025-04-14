from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission # استيراد النماذج المدمجة
from .models import *  # استيراد باقي النماذج مثل Tenant و Domain
from django.utils.html import format_html
from django.utils.html import mark_safe
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import CustomUserCreationForm
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
    fields = ('phone_number', 'address', 'profile_picture')


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    inlines = [UserProfileInline]

    # حدد الحقول في صفحة إضافة المستخدم
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'phone_number', 'address', 'profile_picture'),
        }),
    )

    # حدد الحقول في صفحة تعديل المستخدم
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser'),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'address', 'profile_picture'),
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    def save_model(self, request, obj, form, change):
        """يتم هنا حفظ UserProfile تلقائيًا عند إضافة مستخدم جديد"""
        super().save_model(request, obj, form, change)
        if not change:  # يعني مستخدم جديد
            UserProfile.objects.update_or_create(
                user=obj,
                defaults={
                    'phone_number': form.cleaned_data.get('phone_number'),
                    'address': form.cleaned_data.get('address'),
                    'profile_picture': form.cleaned_data.get('profile_picture')
                }
            )

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
