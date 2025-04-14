# from django.shortcuts import redirect
# from django.utils.deprecation import MiddlewareMixin
# from companies_manager.models import Company

# class TenantMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         domain = request.get_host().split(':')[0]  # استخراج الدومين بدون البورت
#         try:
#             request.tenant = Company.objects.get(domain=domain)  # البحث عن المستأجر
#         except Company.DoesNotExist:
#             return redirect('/')  # إعادة التوجيه للصفحة الرئيسية
