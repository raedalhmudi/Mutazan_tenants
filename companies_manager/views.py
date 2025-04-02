from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django_tenants.utils import schema_context
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Company, WeightCardMain
from .utils import transfer_weight_cards


@csrf_exempt
def fetch_company_data(request, company_id):
    """تشغيل دالة جلب البيانات وإرجاع النتائج كـ JSON بناءً على `company_id`"""
    try:
        company = get_object_or_404(Company, id=company_id)

        # تشغيل نقل البيانات للشركة المحددة فقط
        with schema_context(company.schema_name):
            transfer_weight_cards()
            cards = WeightCardMain.objects.filter(schema_name=company.schema_name).values(
                "plate_number", "empty_weight", "loaded_weight",
                "net_weight", "driver_name", "entry_date",
                "exit_date", "material", "status"
            )

        return JsonResponse({"status": "success", "cards": list(cards)})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


def company_list(request):
    """عرض قائمة الشركات"""
    companies = Company.objects.all()
    return render(request, 'companies/company_list.html', {'companies': companies})


def company_detail(request, company_id):
    """عرض تفاصيل الشركة وبطاقات الوزن الخاصة بها بناءً على schema_name"""
    company = get_object_or_404(Company, id=company_id)

    # التبديل إلى مخطط الشركة الصحيح
    with schema_context(company.schema_name):
        # جلب جميع بطاقات الوزن بناءً على schema_name
        transferred_cards = WeightCardMain.objects.filter(schema_name=company.schema_name)

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'transferred_cards': transferred_cards,
    })




class CustomLoginView(LoginView):
    """عرض مخصص لتسجيل الدخول"""
    template_name = "login.html"

    def form_valid(self, form):
        """ التحقق من أن المستخدم هو المسؤول الإداري لشركة معينة """
        user = form.get_user()
        try:
            tenant = Company.objects.get(admin_user=user)

            # ✅ تبديل Schema إلى الشركة الخاصة به
            with schema_context(tenant.schema_name):
                return super().form_valid(form)  # تسجيل الدخول باستخدام `LoginView`
        except Company.DoesNotExist:
            form.add_error(None, "ليس لديك صلاحية الدخول.")
            return self.form_invalid(form)  # إرجاع خطأ للمستخدم

    def get_success_url(self):
        """ إعادة التوجيه بعد تسجيل الدخول """
        return "/dashboard/"  # يمكنك تغييرها إلى المسار المناسب
