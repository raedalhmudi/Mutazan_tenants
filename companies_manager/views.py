from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django_tenants.utils import schema_context
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from companies_manager.signals import User
from .models import Company, WeightCardMain
from .utils import transfer_weight_cards

# هذا الملف يحتوي على الـ Views الخاصة بالـ API لشركات

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .Serializer import CompanySerializer
from .models import Company
from django.http import Http404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

#------------كود التوكن-----------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username  # يمكنك إضافة بيانات إضافية هنا
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]  # السماح للجميع باستخدام هذه الواجهة

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # التحقق من اسم المستخدم وكلمة المرور
        user = User.objects.filter(username=username).first()

        if user and user.check_password(password):
            # إنشاء توكن JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'refresh': str(refresh),
                'access': str(access_token),
            })
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "تم التحقق بنجاح!"})
    

    
#----------------------كلاس الapi----------------------
# عرض قائمة الشركات أو إضافة شركة جديدة
class CompanyListAPIView(APIView):
    def get(self, request, format=None):
        companies = Company.objects.all()  # جلب كل الشركات
        serializer = CompanySerializer(companies, many=True)  # تحويل البيانات إلى JSON
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CompanySerializer(data=request.data)  # تحويل البيانات القادمة من المستخدم
        if serializer.is_valid():
            serializer.save()  # حفظ الشركة الجديدة
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# عرض تفاصيل شركة معينة أو تعديلها أو حذفها
class CompanyDetailView(APIView):
    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)  # جلب الشركة بناءً على ID
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        company = self.get_object(pk)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()  # حفظ التعديلات
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        company = self.get_object(pk)
        company.delete()  # حذف الشركة
        return Response(status=status.HTTP_204_NO_CONTENT)
    



    
#---------------------------نهايه كلاس الapi-------------



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




# class CustomLoginView(LoginView):
#     """عرض مخصص لتسجيل الدخول"""
#     template_name = "login.html"

#     def form_valid(self, form):
#         """ التحقق من أن المستخدم هو المسؤول الإداري لشركة معينة """
#         user = form.get_user()
#         try:
#             tenant = Company.objects.get(admin_user=user)

#             # ✅ تبديل Schema إلى الشركة الخاصة به
#             with schema_context(tenant.schema_name):
#                 return super().form_valid(form)  # تسجيل الدخول باستخدام `LoginView`
#         except Company.DoesNotExist:
#             form.add_error(None, "ليس لديك صلاحية الدخول.")
#             return self.form_invalid(form)  # إرجاع خطأ للمستخدم

#     def get_success_url(self):
#         """ إعادة التوجيه بعد تسجيل الدخول """
#         return "/dashboard/"  # يمكنك تغييرها إلى المسار المناسب
