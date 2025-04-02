from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import login
from django_tenants.utils import tenant_context
from user_management.models import CustomUser
from .services import generate_sso_token, validate_sso_token
from .models import TenantSSOConfig

def initiate_sso(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'غير مصرح به'}, status=401)
    
    target_tenant = request.GET.get('tenant')
    if not target_tenant:
        return JsonResponse({'error': 'يجب تحديد المستأجر'}, status=400)
    
    try:
        # التحقق من أن المستخدم مسموح له بالوصول إلى هذا المستأجر
        with tenant_context(request.user.managed_company):
            config = TenantSSOConfig.objects.get(tenant__schema_name=target_tenant)
            
        token = generate_sso_token(request.user)
        redirect_url = f"http://{target_tenant}.localhost/sso/validate?token={token}"
        return JsonResponse({'redirect_url': redirect_url})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def validate_sso(request):
    token = request.GET.get('token')
    if not token:
        return JsonResponse({'error': 'رمز SSO مطلوب'}, status=400)
    
    user = validate_sso_token(token)
    if user:
        login(request, user)
        return redirect('/')  # الصفحة الرئيسية بعد تسجيل الدخول
    return JsonResponse({'error': 'رمز SSO غير صالح أو منتهي الصلاحية'}, status=400)