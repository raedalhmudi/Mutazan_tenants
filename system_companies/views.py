from django.db import connection
from django.shortcuts import render, get_object_or_404
from .models import Invoice, WeightCard, Devices
from django.http import StreamingHttpResponse
import cv2
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.contrib.admin.sites import site
from django.db.models import Sum, Count
from .models import WeightCard, ViolationRecord, Entry_and_exit
#------------api----------
from rest_framework import generics
from .models import Invoice
# from .serializer import InvoiceSerializer
from rest_framework import response
# from .models import Invoice
# from .serializers import InvoiceSerializer
from rest_framework.views import APIView
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from .models import Invoice
from .serializers import InvoiceSerializer

class InvoiceListView(APIView):
    def get(self, request):
        schema_name = request.headers.get("X-Schema")
        if not schema_name:
            return Response({"error": "يرجى تحديد اسم السكيمة في الهيدر X-Schema"}, status=400)

        try:
            # طباعة للتأكد من السكيمة الحالية
            print("✅ Switching to schema:", schema_name)
            connection.set_schema(schema_name, include_public=False)

            # تأكد أن الجدول موجود فعلًا في السكيمة
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = %s AND tablename = 'system_companies_invoice'
                """, [schema_name])
                result = cursor.fetchone()
                if not result:
                    return Response({"error": f"الجدول غير موجود في السكيمة '{schema_name}'"}, status=404)

            invoices = Invoice.objects.all()
            serializer = InvoiceSerializer(invoices, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class InvoiceListView(generics.ListAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
from .models import WeightCard, ViolationRecord, Entry_and_exit, Material, DriverNeme, Trucks

from django.shortcuts import render
from django.http import JsonResponse

from django.utils import timezone

@staff_member_required
def reports_view(request):
    cards = WeightCard.objects.all()
    violations = ViolationRecord.objects.all()
    entry_and_exit = Entry_and_exit.objects.all()
    material = Material.objects.all()
    trucks = Trucks.objects.all()

    # قاموس لربط رقم الشاحنة باسم السائق
    truck_lookup = {t.plate_number: t.driver_name for t in trucks}

    # تجهيز بيانات المخالفات مع اسم السائق
    violations_data = []
    for v in violations:
        Trucks.plate_number = v.plate_number_vio
        driver_name = truck_lookup.get(Trucks.plate_number, "غير معروف")
        print(f"مخالفة لشاحنة {Trucks.plate_number} - السائق: {driver_name}")  # <-- سطر مؤقت لفحص البيانات
        violations_data.append({
            "plate_number": Trucks.plate_number,
            "violation_type": v.violation_type,
            "driver_name": driver_name,
        })



    stats = {
        "total_cards": cards.count(),
        "complete_cards": cards.filter(status='complete').count(),
        "incomplete_cards": cards.filter(status='incomplete').count(),
        "total_net_weight": cards.aggregate(Sum('net_weight'))['net_weight__sum'] or 0,
    }

    context = {
        **site.each_context(request),
        "app_list": site.get_app_list(request),
        "cards": cards,
        "violations": violations,  # تمرير قائمة البيانات
        "entry_and_exit": entry_and_exit,
        "material": material,
        "trucks": trucks,
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
    
    # تحديد التاريخ الافتراضي إذا لم يتم تحديد نطاق
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
    
    # تحليل نطاق التاريخ
    dates = date_range.split(' - ')
    start_date = datetime.strptime(dates[0], '%Y-%m-%d').date()
    end_date = datetime.strptime(dates[1], '%Y-%m-%d').date() + timedelta(days=1)  # لتشمل اليوم كامل
    
    # جلب البيانات حسب نوع التقرير مع الفلترة بالتاريخ
    if report_type == 'weight_cards':
        context['cards'] = WeightCard.objects.filter(
            entry_date__gte=start_date,
            entry_date__lte=end_date
        ).order_by('-entry_date')
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
    
    return render(request, 'admin/print_report.html', context)


