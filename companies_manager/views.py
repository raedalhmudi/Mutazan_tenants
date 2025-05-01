from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django_tenants.utils import schema_context
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Company, WeightCardMain
from .utils import transfer_weight_cards, transfer_violations
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from system_companies.models import WeightCard, ViolationRecord
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from companies_manager.admin import tenant_admin_site 


@csrf_exempt
def fetch_company_data(request, company_id):
    """جلب البيانات مباشرة من قاعدة بيانات الشركة دون تخزين مركزي"""
    try:
        company = get_object_or_404(Company, id=company_id)
        data_type = request.GET.get('data_type', 'weight_cards')  # نوع البيانات المطلوبة

        with schema_context(company.schema_name):
            if data_type == 'weight_cards':
                from system_companies.models import WeightCard
                cards_qs = WeightCard.objects.all().select_related('plate_number', 'driver_name', 'material')
                cards = []

                for card in cards_qs:
                    # if not hasattr(card, 'violation_type') or card.violation_type is None:
                        cards.append({
                            "plate_number": card.plate_number.plate_number if card.plate_number else '',
                            "empty_weight": card.empty_weight,
                            "loaded_weight": card.loaded_weight,
                            "net_weight": card.net_weight,
                            "driver_name": card.driver_name.driver_name if card.driver_name else '',
                            "entry_date": card.entry_date,
                            "exit_date": card.exit_date,
                            "quantity": card.quantity,
                            "material": card.material.name_material if card.material else '',
                            "status": card.status,
                            "violation_type": ""
                        })

            else:  # violations
                from system_companies.models import ViolationRecord
                violations = ViolationRecord.objects.all().select_related(
                    'plate_number_vio', 'violation_type', 'device_vio',
                    'entry_exit_log', 'weight_card_vio',
                )

                cards = []
                for violation in violations:
                    cards.append({
                        'plate_number': violation.plate_number_vio.plate_number if violation.plate_number_vio else '',
                        'violation_type': violation.violation_type.name if violation.violation_type else '',
                        'timestamp': violation.timestamp,
                        'device_vio': violation.device_vio.name if violation.device_vio else '',
                        'entry_exit_log': str(violation.entry_exit_log.id) if violation.entry_exit_log else '',
                        'weight_card_vio': str(violation.weight_card_vio.id) if violation.weight_card_vio else '',
                        ''
                        'status': 'complete',
                        'created_at': violation.timestamp
                    })

        return JsonResponse({"status": "success", "cards": cards, "data_type": data_type})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@staff_member_required
def company_list(request):
    """عرض قائمة الشركات مع عدد الشاحنات في كل شركة"""
    companies = Company.objects.all()
    enriched_companies = []

    for company in companies:
        truck_count = 0

        try:
            with schema_context(company.schema_name):
                from system_companies.models import Trucks,Invoice  # تأكد من اسم الموديل
                truck_count = Trucks.objects.count()
                invoices_count = Invoice.objects.count()
                violations_count = ViolationRecord.objects.count()
        except Exception as e:
            print(f"⚠️ خطأ في {company.company_name}: {e}")
            truck_count = 0
            invoices_count = 0
            violations_count = 0

        # بناء dict يحتوي البيانات المطلوبة للقالب
        enriched_companies.append({
            'id': company.id,
            'company_name': company.company_name,
            'logo': company.logo,
            'services_offered': company.services_offered,
            'violations': violations_count,  # يمكنك تحديثها لاحقًا
            'invoices': invoices_count,    # يمكنك تحديثها لاحقًا
            'trucks': truck_count
        })

    context = {
        **tenant_admin_site.each_context(request),
        "app_list": tenant_admin_site.get_app_list(request),
        "companies": enriched_companies,  # هذا المهم
    }

    return TemplateResponse(request, 'companies/company_list.html', context)

@staff_member_required
def company_detail(request, company_id):
    """عرض تفاصيل الشركة وبطاقات الوزن الخاصة بها بناءً على schema_name"""
    company = get_object_or_404(Company, id=company_id)

    # التبديل إلى مخطط الشركة الصحيح
    with schema_context(company.schema_name):
        # جلب جميع بطاقات الوزن بناءً على schema_name
        transferred_cards = WeightCardMain.objects.filter(schema_name=company.schema_name)
    
    context = {
        **tenant_admin_site.each_context(request),
        "app_list": tenant_admin_site.get_app_list(request),
        'company': company,
        'transferred_cards': transferred_cards,
    }

    return render(request, 'companies/company_detail.html', context)




class CustomLoginView(LoginView):
    """عرض مخصص لتسجيل الدخول"""
    template_name = "login.html"

    def form_valid(self, form):
        user = form.get_user()
        from django.db import connection
        print("✅ Trying login")
        print("📍 Current schema:", connection.schema_name)
        print("👤 Username:", user.username)
        print("👤 Is staff:", user.is_staff)
        print("👤 Is superuser:", user.is_superuser)

        if user.is_superuser:
            return super().form_valid(form)

        try:
            tenant = Company.objects.get(admin_user=user)
            with schema_context(tenant.schema_name):
                return super().form_valid(form)
        except Company.DoesNotExist:
            form.add_error(None, "🚫 لا تملك صلاحية الدخول.")
            return self.form_invalid(form)


    def get_success_url(self):
        """ إعادة التوجيه بعد تسجيل الدخول """
        return "/dashboard/"  # يمكنك تغييرها إلى المسار المناسب




@csrf_exempt
def print_weight_cards(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    try:
        with schema_context(company.schema_name):
            report_type = request.GET.get('report_type', 'daily')
            data_type = request.GET.get('data_type', 'weight_cards')
            
            if data_type == 'weight_cards':
                # تعديل: جلب بطاقات الوزن مباشرة من جدول WeightCard بدلاً من WeightCardMain
                queryset = WeightCard.objects.all()
                date_field = 'entry_date'
                report_title = "تقرير بطاقات الوزن"
            else:
                # جلب المخالفات مباشرة من جدول ViolationRecord
                queryset = ViolationRecord.objects.all()
                date_field = 'timestamp'
                report_title = "تقرير المخالفات"
            
            # تطبيق الفلترة حسب نوع التقرير
            if report_type == 'daily':
                date_str = request.GET.get('date', timezone.now().date().isoformat())
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(**{f'{date_field}__date': date})
                report_title += f" اليومي - {date}"
            
            elif report_type == 'weekly':
                today = timezone.now().date()
                from_date = request.GET.get('from_date', (today - timedelta(days=today.weekday())).isoformat())
                to_date = request.GET.get('to_date', (today + timedelta(days=6 - today.weekday())).isoformat())
                
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                
                queryset = queryset.filter(
                    **{f'{date_field}__date__gte': from_date},
                    **{f'{date_field}__date__lte': to_date}
                )
                report_title += f" الأسبوعي من {from_date} إلى {to_date}"
            
            elif report_type == 'monthly':
                today = timezone.now().date()
                month = request.GET.get('month', today.month)
                year = request.GET.get('year', today.year)
                
                queryset = queryset.filter(
                    **{f'{date_field}__month': month},
                    **{f'{date_field}__year': year}
                )
                report_title += f" الشهري - {month}/{year}"
            
            # تحضير البيانات للعرض
            if data_type == 'weight_cards':
                # تعديل: تجهيز بيانات بطاقات الوزن من WeightCard بنفس تنسيق بيانات المخالفات
                transferred_cards = []
                for card in queryset:
                    transferred_cards.append({
                        "plate_number": card.plate_number.plate_number if card.plate_number else '',
                        "empty_weight": card.empty_weight,
                        "loaded_weight": card.loaded_weight,
                        "net_weight": card.net_weight,
                        "driver_name": card.driver_name.driver_name if card.driver_name else '',
                        "entry_date": card.entry_date,
                        "exit_date": card.exit_date,
                        "material": card.material.name_material if card.material else '',
                        "status": card.status,
                    })
            else:
                transferred_cards = []
                for violation in queryset:
                    transferred_cards.append({
                        'plate_number': violation.plate_number_vio.plate_number if violation.plate_number_vio else '',
                        'violation_type': violation.violation_type.name if violation.violation_type else '',
                        'timestamp': violation.timestamp,
                        'device_vio': violation.device_vio.name if violation.device_vio else '',
                        'entry_exit_log': str(violation.entry_exit_log) if violation.entry_exit_log else '',
                        'weight_card_vio': str(violation.weight_card_vio) if violation.weight_card_vio else '',
                        'status': 'complete'
                    })
            
            return render(request, 'companies/print_weight_cards.html', {
                'company': company,
                'transferred_cards': transferred_cards,
                'report_title': report_title,
                'data_type': data_type
            })
            
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
        messages.error(request, f"حدث خطأ في جلب البيانات: {str(e)}")
        return redirect('company_detail', company_id=company_id)
# -------------------------------------------





