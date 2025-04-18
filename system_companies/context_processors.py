# from django_tenants.utils import get_tenant

# def company_info(request):
#     try:
#         tenant = get_tenant(request)
#         return {
#             'COMPANY_NAME': tenant.company_name if tenant else "إدارة النظام",
#             'COMPANY_LOGO': tenant.logo.url if tenant and tenant.logo else None
#         }
#     except Exception as e:
#         return {
#             'COMPANY_NAME': "إدارة النظام",
#             'COMPANY_LOGO': None
#         }