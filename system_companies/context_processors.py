# from django.db import connection

# def current_tenant(request):
#     tenant_name = "النظام الرئيسي"  # القيمة الافتراضية

#     if hasattr(connection, 'tenant') and connection.tenant:
#         tenant = connection.tenant
#         tenant_name = getattr(tenant, 'company_name', tenant_name)

#     print(f"Current Tenant Schema: {connection.schema_name}")  # لطباعة الـ schema الحالي
#     return {"tenant_name": tenant_name}
