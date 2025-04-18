# #طلب الفواتير من تطبيق الشركات

# import requests
# from django.conf import settings

# def fetch_invoices(access_token):
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'X-Tenant': 'tenant_schema'  # إضافة معرف المستأجر
#     }
#     try:
#         response = requests.get(
#             f'{settings.SYSTEM_COMPANIES_URL}/api/invoices/',
#             headers=headers
#         )
#         return response.json() if response.status_code == 200 else []
#     except requests.exceptions.RequestException:
#         return []