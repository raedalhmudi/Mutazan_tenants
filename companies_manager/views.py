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
from django.contrib.auth import logout
from system_companies.models import WeightCard, ViolationRecord, Entry_and_exit
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from companies_manager.admin import tenant_admin_site 

@csrf_exempt
def fetch_company_data(request, company_id):
    try:
        company = get_object_or_404(Company, id=company_id)
        data_type = request.GET.get('data_type', 'weight_cards')

        with schema_context(company.schema_name):
            if data_type == 'weight_cards':
                cards_qs = WeightCard.objects.all().select_related('plate_number', 'driver_name').prefetch_related('materials__material')

                cards = []
                for card in cards_qs:
                    # جلب المواد والكميات المرتبطة بالبطاقة
                    materials = []
                    quantities = []
                    for wm in card.materials.all():
                        if wm.material:
                            materials.append(wm.material.name_material)
                            quantities.append(wm.quantity)

                    cards.append({
                        "plate_number": card.plate_number.plate_number if card.plate_number else '',
                        "empty_weight": card.empty_weight,
                        "loaded_weight": card.loaded_weight,
                        "net_weight": card.net_weight,
                        "driver_name": card.driver_name.driver_name if card.driver_name else '',
                        "entry_date": card.entry_date,
                        "exit_date": card.exit_date,
                        "status": card.status,
                        "materials": materials,
                        "quantities": quantities,
                        "violation_type": ""
                    })

            elif data_type == 'violations':
                from system_companies.models import ViolationRecord, Legal_weight
                violations = ViolationRecord.objects.all().select_related(
                    'plate_number_vio', 'violation_type', 'device_vio',
                    'entry_exit_log', 'weight_card_vio', 'weight_card_vio__plate_number'
                )

                cards = []
                for violation in violations:
                    try:
                        if violation.violation_type.name == 'Exceeding the legal weight':
                            weight_card = violation.weight_card_vio
                            if weight_card and weight_card.loaded_weight and weight_card.empty_weight:
                                net_weight = weight_card.loaded_weight - weight_card.empty_weight
                                try:
                                    legal_weight_entry = Legal_weight.objects.get(
                                        number_of_axes=weight_card.plate_number.number_of_axles
                                    )
                                    legal_weight = legal_weight_entry.legal_weight_L_W
                                    if weight_card.loaded_weight > legal_weight:
                                        excess_weight = weight_card.loaded_weight - legal_weight
                                        penalty = excess_weight * violation.violation_type.penalty_amount
                                    else:
                                        penalty = 0.00
                                except Legal_weight.DoesNotExist:
                                    penalty = violation.violation_type.penalty_amount
                            else:
                                penalty = violation.violation_type.penalty_amount
                        else:
                            penalty = violation.violation_type.penalty_amount
                    except Exception:
                        penalty = violation.violation_type.penalty_amount

                    cards.append({
                        'plate_number': violation.plate_number_vio.plate_number if violation.plate_number_vio else '',
                        'violation_type': violation.violation_type.name if violation.violation_type else '',
                        'timestamp': violation.timestamp,
                        'device_vio': violation.device_vio.name if violation.device_vio else '',
                        'entry_exit_log': str(violation.entry_exit_log.id) if violation.entry_exit_log else '',
                        'weight_card_vio': str(violation.weight_card_vio.id) if violation.weight_card_vio else '',
                        'status': 'complete',
                        'created_at': violation.timestamp,
                        'penalty_amount': f"{penalty:.2f} $"
                    })

            elif data_type == 'entry_exit_logs':
                # جلب بيانات عمليات الدخول والخروج
                logs_qs = Entry_and_exit.objects.all().select_related(
                    'plate_number_E_e', 'device'
                )

                cards = []
                for log in logs_qs:
                    cards.append({
                        'process_type': log.get_name_display(),
                        'plate_number': log.plate_number_E_e.plate_number if log.plate_number_E_e else '',
                        'camera': log.device.name if log.device else '',
                        'entry_date': log.entry_date,
                        'exit_date': log.exit_date,
                        'status': log.get_pruss_status_display(),
                        'entry_image': log.image_path_entry.url if log.image_path_entry else '',
                        'exit_image': log.image_path_exit.url if log.image_path_exit else '',
                        'process_status': 'complete' if log.pruss_status == 'complete' else 'incomplete'
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
                from system_companies.models import Trucks, Invoice  # تأكد من اسم الموديل
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




# from system_companies.models import WeightCard, ViolationRecord  # تأكد من المسار الصحيح

@csrf_exempt
def print_weight_cards(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    try:
        with schema_context(company.schema_name):
            report_type = request.GET.get('report_type', 'daily')
            data_type = request.GET.get('data_type', 'weight_cards')
            
            if data_type == 'weight_cards':
                # تغيير هنا: إزالة material من select_related وإضافة prefetch_related للمواد
                queryset = WeightCard.objects.all().select_related('plate_number', 'driver_name').prefetch_related('materials__material')
                date_field = 'entry_date'
                report_title = "تقرير بطاقات الوزن"

            elif data_type == 'violations':
                queryset = ViolationRecord.objects.all().select_related(
                    'plate_number_vio', 'violation_type', 'device_vio',
                    'entry_exit_log', 'weight_card_vio'
                )
                date_field = 'timestamp'
                report_title = "تقرير المخالفات"
            elif data_type == 'entry_exit_logs':
                
                queryset = Entry_and_exit.objects.all().select_related(
                    'plate_number_E_e', 'device')
                date_field = 'entry_date'
                report_title = "تقرير عمليات الدخول الخروج"
            
            # تطبيق الفلترة حسب نوع التقرير
            if report_type == 'daily':
                date_str = request.GET.get('date', timezone.now().date().isoformat())
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(**{f'{date_field}__date': date})
                report_title += f" اليومي - {date.strftime('%Y-%m-%d')}"
            
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
                report_title += f" الأسبوعي من {from_date.strftime('%Y-%m-%d')} إلى {to_date.strftime('%Y-%m-%d')}"
            
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
            cards = []
            for item in queryset:
                if data_type == 'weight_cards':
                    # معالجة المواد والكميات باستخدام prefetch_related
                    materials = []
                    for wm in item.materials.all():  # هذه تعمل بسبب prefetch_related
                        materials.append(f"{wm.material.name_material if wm.material else 'غير محدد'} ({wm.quantity})")
                    
                    cards.append({
                        "plate_number": item.plate_number.plate_number if item.plate_number else 'غير محدد',
                        "empty_weight": item.empty_weight,
                        "loaded_weight": item.loaded_weight,
                        "net_weight": item.net_weight,
                        "driver_name": item.driver_name.driver_name if item.driver_name else 'غير محدد',
                        "entry_date": item.entry_date,
                        "exit_date": item.exit_date,
                        "status": item.status,
                        "material": " / ".join(materials) if materials else 'غير محدد',
                        "quantity": "",  # الكميات مدرجة في حقل المواد
                    })
                elif data_type == 'violations':
                    cards.append({
                        'plate_number': item.plate_number_vio.plate_number if item.plate_number_vio else 'غير محدد',
                        'violation_type': item.violation_type.name if item.violation_type else 'غير محدد',
                        'timestamp': item.timestamp,
                        'device_vio': item.device_vio.name if item.device_vio else 'غير محدد',
                        'entry_exit_log': str(item.entry_exit_log) if item.entry_exit_log else 'غير محدد',
                        'weight_card_vio': str(item.weight_card_vio) if item.weight_card_vio else 'غير محدد',
                        'status': item.status if hasattr(item, 'status') else 'مكتمل'
                    })
                elif data_type == 'entry_exit_logs':
                    cards.append({
                        'process_type': item.get_name_display(),
                        'plate_number': item.plate_number_E_e.plate_number if item.plate_number_E_e else '',
                        'camera': item.device.name if item.device else '',
                        'entry_date': item.entry_date,
                        'exit_date': item.exit_date,
                        'status': item.get_pruss_status_display(),
                        'entry_image': item.image_path_entry.url if item.image_path_entry else '',
                        'exit_image': item.image_path_exit.url if item.image_path_exit else '',
                        'process_status': 'complete' if item.pruss_status == 'complete' else 'incomplete'
                    })
            
            context = {
                'company': company,
                'transferred_cards': cards,
                'report_title': report_title,
                'data_type': data_type,
                'now': timezone.now()
            }
            
            return render(request, 'companies/print_weight_cards.html', context)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"حدث خطأ في جلب البيانات: {str(e)}")
        return redirect('company_detail', company_id=company_id)
    


def logout_view(request):
    logout(request)
    return redirect('logout_complete')

def logout_complete(request):
    return render(request, 'logout_complete.html')