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

# import threading
# from django.db import connection

# _local = threading.local()

# class DynamicSchemaMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # استخراج اسم الشركة من:
#         # - subdomain (company1.yoursite.com)
#         # - header (X-Company-Name)
#         # - JWT token
#         company_name = request.META.get('HTTP_X_COMPANY_NAME', 'public')
        
#         set_company_schema(company_name)
#         response = self.get_response(request)
#         reset_schema()
#         return response

# def set_company_schema(schema):
#     _local.schema = schema
#     with connection.cursor() as cursor:
#         cursor.execute(f"SET search_path TO {schema},public")

# def get_current_schema():
#     return getattr(_local, 'schema', 'public')

# def reset_schema():
#     with connection.cursor() as cursor:
#         cursor.execute("SET search_path TO public")
from django.utils.deprecation import MiddlewareMixin
from django.db import connection

class SchemaMiddleware(MiddlewareMixin):
    def process_request(self, request):
        schema = request.headers.get('X-Schema')
        if schema:
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO {schema}, public')