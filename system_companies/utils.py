from .models import ActivityLog

def log_action(request, action, module="", extra_data=""):
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        module=module,
        ip_address=get_client_ip(request),
        extra_data=extra_data
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
