def company_context(request):
    tenant = getattr(request, 'tenant', None)
    return {
        "tenant": tenant,
        "company_name": getattr(tenant, 'company_name', 'اسم الشركة'),
        "logo_url": tenant.logo.url if tenant and hasattr(tenant, 'logo') and tenant.logo else '/static/default-logo.png'
    }
