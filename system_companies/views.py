from django.shortcuts import render, get_object_or_404, redirect
from .models import Invoice, WeightCard, Devices
from django.http import StreamingHttpResponse
import cv2
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.contrib.admin.sites import site
from django.db.models import Sum, Count
from .models import WeightCard, ViolationRecord, Entry_and_exit, Material, DriverNeme, Trucks, WeightCardMaterial
from companies_manager.models import ViolationsType, Legal_weight
from .utils import log_action
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Prefetch
# 
from django.contrib.auth import logout

@staff_member_required
def reports_view(request):
    cards_qs = WeightCard.objects.all().select_related('plate_number', 'driver_name').prefetch_related(
        Prefetch('materials', queryset=WeightCardMaterial.objects.select_related('material'))
    )
    violations = ViolationRecord.objects.select_related(
        'violation_type', 'plate_number_vio', 'weight_card_vio__plate_number'
    ).all()
    
    entry_and_exit = Entry_and_exit.objects.all()
    material = Material.objects.all()
    trucks = Trucks.objects.all()
    driverneme = DriverNeme.objects.all()
    invoice = Invoice.objects.all() 

    # قاموس لربط رقم الشاحنة باسم السائق
    truck_lookup = {t.plate_number: t.driver_name for t in trucks}

    # تعديل كائنات المخالفات لإضافة قيمة الغرامة المحتسبة
    for v in violations:
        try:
            if v.violation_type.name == 'Exceeding the legal weight':
                weight_card = v.weight_card_vio
                if weight_card and weight_card.loaded_weight and weight_card.empty_weight:
                    net_weight = weight_card.loaded_weight - weight_card.empty_weight
                    legal_weight_entry = Legal_weight.objects.get(
                        number_of_axes=weight_card.plate_number.number_of_axles
                    )
                    legal_weight = legal_weight_entry.legal_weight_L_W

                    if weight_card.loaded_weight > legal_weight:
                        excess_weight = weight_card.loaded_weight - legal_weight
                        penalty = excess_weight * v.violation_type.penalty_amount
                        v.penalty_amount_calculated = f"{penalty:.2f} $"
                    else:
                        v.penalty_amount_calculated = "0.00 $"
                else:
                    # بيانات بطاقة الوزن غير كافية، fallback إلى القيمة الثابتة
                    v.penalty_amount_calculated = f"{v.violation_type.penalty_amount:.2f} $"
            else:
                # مخالفات أخرى → استخدم قيمة الغرامة من نوع المخالفة
                v.penalty_amount_calculated = f"{v.violation_type.penalty_amount:.2f} $"
        except Exception:
            # fallback في حال وجود خطأ
            v.penalty_amount_calculated = f"{v.violation_type.penalty_amount:.2f} $"

    # تجهيز بيانات بطاقات الوزن
    cards_data = []
    for card in cards_qs:
        materials_list = []
        quantities_list = []

        for wm in card.materials.all():
            if wm.material:
                materials_list.append(wm.material.name_material)
                quantities_list.append(str(wm.quantity))

        cards_data.append({
            "plate_number": card.plate_number.plate_number if card.plate_number else '',
            "driver_name": card.driver_name.driver_name if card.driver_name else '',
            "entry_date": card.entry_date,
            "exit_date": card.exit_date,
            "status": card.status,
            "empty_weight": card.empty_weight,
            "loaded_weight": card.loaded_weight,
            "net_weight": card.net_weight,
            "materials": materials_list,
            "quantities": quantities_list,
        })

    stats = {
        "total_cards": cards_qs.count(),
        "complete_cards": cards_qs.filter(status='complete').count(),
        "incomplete_cards": cards_qs.filter(status='incomplete').count(),
        "total_net_weight": cards_qs.aggregate(Sum('net_weight'))['net_weight__sum'] or 0,
    }
    from datetime import datetime

# التاريخ الحالي
    now = datetime.now()

    # تصفية المخالفات الخاصة بالشهر الحالي فقط
    violations_this_month = violations.filter(timestamp__year=now.year, timestamp__month=now.month)

    # حساب مجموع الغرامات للشهر الحالي
    total_monthly_penalty = 0
    for v in violations_this_month:
        try:
            if v.violation_type.name == 'Exceeding the legal weight':
                weight_card = v.weight_card_vio
                if weight_card and weight_card.loaded_weight and weight_card.empty_weight:
                    net_weight = weight_card.loaded_weight - weight_card.empty_weight
                    legal_weight_entry = Legal_weight.objects.get(
                        number_of_axes=weight_card.plate_number.number_of_axles
                    )
                    legal_weight = legal_weight_entry.legal_weight_L_W

                    if weight_card.loaded_weight > legal_weight:
                        excess_weight = weight_card.loaded_weight - legal_weight
                        penalty = excess_weight * v.violation_type.penalty_amount
                        total_monthly_penalty += penalty
                    else:
                        total_monthly_penalty += 0
                else:
                    total_monthly_penalty += v.violation_type.penalty_amount
            else:
                total_monthly_penalty += v.violation_type.penalty_amount
        except Exception:
            total_monthly_penalty += v.violation_type.penalty_amount


    context = {
        **site.each_context(request),
        "app_list": site.get_app_list(request),
        "cards": cards_data,
        "violations": violations,  # ← الآن كل عنصر فيه penalty_amount_calculated
        "entry_and_exit": entry_and_exit,
        "material": material,
        "trucks": trucks,
        "driverneme": driverneme,
        "total_monthly_penalty": total_monthly_penalty,
        "invoice": invoice,
        "stats": stats,
    }

    return TemplateResponse(request, "admin/reports.html", context)


# دالة توليد الإطارات من الكاميرا
def generate_frames(ip, username, password):
    url = f"rtsp://{username}:{password}@{ip}:554/stream"
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print(f"❌ Failed to open camera at {url}")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("❌ Failed to read frame from camera")
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

# دالة عرض البث في المسار `/video_feed/<location>/`
def video_feed(request, location):
    camera = Devices.objects.filter(location=location).first()
    
    if not camera or not camera.address_ip:
        return StreamingHttpResponse("⚠️ لا يوجد بث لهذه الكاميرا", content_type="text/plain")

    try:
        return StreamingHttpResponse(
            generate_frames(camera.address_ip, "admin", "1234567890"),
                        # generate_frames(camera.address_ip, camera.username, camera.password),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return StreamingHttpResponse(f"⚠️ خطأ في تشغيل البث: {str(e)}", content_type="text/plain")






def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'admin/invoice_list.html', {'invoices': invoices})

def invoice_print_modal(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'admin/invoice_modal.html', {'invoice': invoice})



    
from django.utils import timezone
from datetime import datetime, timedelta
def print_report(request):
    report_type = request.GET.get('report_type', 'weight_cards')
    report_title = request.GET.get('title', 'تقرير')
    date_range = request.GET.get('date_range', '')

    if not date_range:
        today = timezone.now().date()
        last_month = today - timedelta(days=30)
        date_range = f"{last_month.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}"

    context = {
        'report_type': report_type,
        'report_title': report_title,
        'report_date': date_range,
        'company': {'name': 'اسم الشركة'},
    }

    dates = date_range.split(' - ')
    start_date = datetime.strptime(dates[0], '%Y-%m-%d').date()
    end_date = datetime.strptime(dates[1], '%Y-%m-%d').date() + timedelta(days=1)

    if report_type == 'weight_cards':
        cards_qs = WeightCard.objects.filter(
            entry_date__gte=start_date,
            entry_date__lte=end_date
        ).select_related('plate_number', 'driver_name').prefetch_related(
            Prefetch('materials', queryset=WeightCardMaterial.objects.select_related('material'))
        ).order_by('-entry_date')

        cards_data = []
        for card in cards_qs:
            materials_list = []
            quantities_list = []

            for wm in card.materials.all():
                if wm.material:
                    materials_list.append(wm.material.name_material)
                    quantities_list.append(str(wm.quantity))

            cards_data.append({
                "plate_number": card.plate_number.plate_number if card.plate_number else '',
                "driver_name": card.driver_name.driver_name if card.driver_name else '',
                "entry_date": card.entry_date,
                "exit_date": card.exit_date,
                "status": card.status,
                "empty_weight": card.empty_weight,
                "loaded_weight": card.loaded_weight,
                "net_weight": card.net_weight,
                "materials": materials_list,
                "quantities": quantities_list,
            })

        context['cards'] = cards_data

    elif report_type == 'violations':
        context['violations'] = ViolationRecord.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('-timestamp')

    elif report_type == 'entry_and_exit':
        context['entry_and_exit'] = Entry_and_exit.objects.filter(
            entry_date__gte=start_date,
            entry_date__lte=end_date
        ).order_by('-entry_date')

    elif report_type == 'material':
        context['material'] = Material.objects.filter(
            date_and_time__gte=start_date,
            date_and_time__lte=end_date
        ).order_by('-date_and_time')

    elif report_type == 'trucks':
        context['trucks'] = Trucks.objects.filter(
            registration_date__gte=start_date,
            registration_date__lte=end_date
        ).order_by('-registration_date')

    elif report_type == 'driverneme':
        context['driverneme'] = DriverNeme.objects.filter(
            date_of_registration__gte=start_date,
            date_of_registration__lte=end_date
        ).order_by('-date_of_registration')

    elif report_type == 'invoice':
        context['invoice'] = Invoice.objects.filter(
            datetime__gte=start_date,
            datetime__lte=end_date
        ).order_by('-datetime')

    return render(request, 'admin/print_report.html', context)

# ----------------------------------------------------------
# --------------------------سجل النشاطات --------------------------------


# def add_truck_view(request):
#     if request.method == "POST":
#         # منطق إضافة الشاحنة هنا
        
#         # سجل النشاط بعد النجاح
#         log_action(request, "إضافة شاحنة جديدة", module="الشاحنات", extra_data="رقم اللوحة: 123ABC")
        
# # ----------------------------------------------------------


# system_companies/views.py


def logout_view(request):
    logout(request)
    return redirect('logout_complete')  # بعد الخروج يتم إعادة التوجيه لهذه الصفحة

def logout_complete(request):
    return render(request, 'logout_complete.html')  # عرض صفحة تأكيد الخروج
