# middleware/jazzmin_dynamic_settings.py
from django.conf import settings
from django.db import connection
import threading

class JazzminDynamicSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'tenant') and connection.schema_name != 'public':
            company = request.tenant
            settings.JAZZMIN_SETTINGS["site_title"] = f"لوحة إدارة {company.company_name}"
            settings.JAZZMIN_SETTINGS["site_header"] = f"لوحة إدارة {company.company_name}"
            settings.JAZZMIN_SETTINGS["site_brand"] = company.company_name
            if company.logo:
                settings.JAZZMIN_SETTINGS["site_logo"] = company.logo.url
            else:
                settings.JAZZMIN_SETTINGS["site_logo"] = "/static/admin/img/logo.png"
        return self.get_response(request)






_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class ThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
