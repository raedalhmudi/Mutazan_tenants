# from companies_manager.models import Company

# def get_current_company_logo(user):
#     try:
#         # لو كنت مخزن الشركة في الجلسة:
#         from django.contrib.sites.shortcuts import get_current_site
#         request = user._request if hasattr(user, "_request") else None
#         company_id = request.session.get("company_id") if request else None
#         company = Company.objects.get(id=company_id) if company_id else None
#         return company.logo.url if company and company.logo else "company_logos/%Y/%m/%d"
#     except Exception:
#         return "company_logos/%Y/%m/%d"
