# # middleware/dynamic_jazzmin.py

# from django.conf import settings

# class DynamicJazzminMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         tenant = getattr(request, 'tenant', None)
#         if tenant and hasattr(settings, 'JAZZMIN_SETTINGS'):
#             settings.JAZZMIN_SETTINGS["site_title"] = tenant.company_name
#             settings.JAZZMIN_SETTINGS["site_header"] = tenant.company_name
#             settings.JAZZMIN_SETTINGS["welcome_sign"] = f"مرحباً بك في {tenant.company_name}"

#         return self.get_response(request)
