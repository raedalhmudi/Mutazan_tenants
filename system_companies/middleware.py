# # from django.shortcuts import redirect
# # from django.utils.deprecation import MiddlewareMixin
# # from companies_manager.models import Company
# from django.utils.functional import SimpleLazyObject
# from django.conf import settings

# class TenantAwareJazzminMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # تحديث إعدادات jazzmin ديناميكيًا
#         def get_dynamic_site_header():
#             try:
#                 # الحصول على المستأجر الحالي
#                 from companies_manager.models import Company
#                 tenant = Company.objects.get(schema_name=request.tenant.schema_name)
#                 return tenant.company_name
#             except Exception:
#                 return "النظام الرئيسي"

#         # تحديث إعدادات jazzmin
#         settings.JAZZMIN_SETTINGS['site_header'] = SimpleLazyObject(get_dynamic_site_header)

#         response = self.get_response(request)
#         return response


# # class TenantMiddleware(MiddlewareMixin):
# #     def process_request(self, request):
# #         domain = request.get_host().split(':')[0]  # استخراج الدومين بدون البورت
# #         try:
# #             request.tenant = Company.objects.get(domain=domain)  # البحث عن المستأجر
# #         except Company.DoesNotExist:
# #             return redirect('/')  # إعادة التوجيه للصفحة الرئيسية
