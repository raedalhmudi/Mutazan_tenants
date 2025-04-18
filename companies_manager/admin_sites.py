# companies_manager/admin_sites.py
from django.contrib.admin import AdminSite
from django.utils import timezone
from django.contrib.auth.models import User
from companies_manager.models import Company

class CompanyAdminSite(AdminSite):
    site_header = "لوحة تحكم الشركات"
    index_template = "companies/custom_index.html"

    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        today = timezone.now().date()
        extra_context['company_count'] = Company.objects.filter(entry_date__date=today).count()
        extra_context['user_count'] = User.objects.count()

        return super().index(request, extra_context)

company_admin_site = CompanyAdminSite(name='company_admin')
