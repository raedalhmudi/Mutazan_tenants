import secrets
from datetime import datetime, timedelta
from django_tenants.utils import tenant_context
from .models import SSOToken

def generate_sso_token(user, expiration_minutes=5):
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now() + timedelta(minutes=expiration_minutes)
    
    # حفظ الرمز في المخطط العام
    sso_token = SSOToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    
    # حفظ الرمز في كل مخطط مستأجر مرتبط بالمستخدم
    if hasattr(user, 'managed_company') and user.managed_company:
        with tenant_context(user.managed_company):
            SSOToken.objects.create(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
    
    return token

def validate_sso_token(token):
    try:
        # التحقق من المخطط العام أولاً
        sso_token = SSOToken.objects.get(
            token=token,
            is_used=False,
            expires_at__gte=datetime.now()
        )
        sso_token.is_used = True
        sso_token.save()
        return sso_token.user
    except SSOToken.DoesNotExist:
        return None