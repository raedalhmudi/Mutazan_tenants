# from django_tenants.utils import tenant_context
# from companies_manager.models import UserProfile

# def get_tenant_user_admin():
#     from django.contrib import admin
#     from django.contrib.auth.models import User
    
#     class TenantUserProfileInline(admin.StackedInline):
#         model = UserProfile
#         extra = 1
#         can_delete = False
#         verbose_name_plural = 'الملف الشخصي'
#         fields = ('profile_picture', 'phone_number', 'address')

#     class TenantUserAdmin(admin.ModelAdmin):
#         inlines = (TenantUserProfileInline,)
        
#         def save_model(self, request, obj, form, change):
#             with tenant_context(request.tenant):
#                 super().save_model(request, obj, form, change)

#     return TenantUserAdmin

# # تسجيل النموذج في كل مستأجر
# def register_tenant_admin():
#     from django.contrib import admin
#     from django.contrib.auth.models import User
    
#     TenantUserAdmin = get_tenant_user_admin()
    
#     try:
#         admin.site.unregister(User)
#     except admin.sites.NotRegistered:
#         pass
        
#     admin.site.register(User, TenantUserAdmin)