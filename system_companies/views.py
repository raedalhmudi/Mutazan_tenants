from django.shortcuts import render, get_object_or_404
from .models import Invoice, WeightCard, Devices
from django.http import StreamingHttpResponse
import cv2
from django.http import JsonResponse
from django.shortcuts import render

#------------api----------
from rest_framework import generics
from .models import Invoice
from .serializers import InvoiceSerializer
from rest_framework import generics
from .models import Invoice
from .serializers import InvoiceSerializer



class InvoiceListView(generics.ListAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# from .models import CustomUser
# from .serializers import UserSerializer

# class CreateUserView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if not request.user.is_company_admin:
#             return Response({"error": "ليس لديك صلاحية لإضافة مستخدمين"}, status=status.HTTP_403_FORBIDDEN)

#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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
    

