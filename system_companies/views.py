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

@staff_member_required
def reports_view(request):
    cards = WeightCard.objects.all()
    violations = ViolationRecord.objects.all()
    entry_and_exit = Entry_and_exit.objects.all()

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
        "violations": violations,
        "entry_and_exit": entry_and_exit,
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


# def company_list(request):
#     companies = Company.objects.all()
#     return render(request, 'companies/company_list.html', {'companies': companies})

# def company_detail(request, company_id):
#     company = get_object_or_404(Company, id=company_id)
#     weight_cards = WeightCard.objects.filter(company=company)  # جلب بطاقات الوزن الخاصة بالشركة
    
#     context = {
#         'company': company,
#         'weight_cards': weight_cards,
#     }
#     return render(request, 'companies/company_detail.html', context)
    













