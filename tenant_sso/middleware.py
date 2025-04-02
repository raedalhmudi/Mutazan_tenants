from django.shortcuts import redirect
from django.urls import reverse
from django_tenants.utils import get_tenant_model

class SSOMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # تخطي إذا كان المستخدم مسجل دخول بالفعل
        if request.user.is_authenticated:
            return None
        
        # تخطي واجهات SSO نفسها
        if request.path.startswith('/sso/'):
            return None
        
        # التحقق من وجود رمز SSO في الكوكيز أو الجلسة
        sso_token = request.COOKIES.get('sso_token') or request.session.get('sso_token')
        if sso_token:
            from .services import validate_sso_token
            user = validate_sso_token(sso_token)
            if user:
                from django.contrib.auth import login
                login(request, user)
                return None
        
        # إذا كان الطلب من نطاق فرعي ولكن بدون مصادقة
        host = request.get_host().split(':')[0]
        if '.' in host and not request.user.is_authenticated:
            main_domain = host.split('.')[0]
            TenantModel = get_tenant_model()
            try:
                tenant = TenantModel.objects.get(schema_name=main_domain)
                # إعادة توجيه إلى صفحة بدء SSO
                sso_url = f"http://{request.user.managed_company.schema_name}.localhost/sso/initiate?tenant={main_domain}"
                return redirect(sso_url)
            except TenantModel.DoesNotExist:
                pass
        
        return None