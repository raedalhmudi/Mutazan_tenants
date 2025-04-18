from django.urls import path
from .views import company_list, company_detail, fetch_company_data, print_weight_cards
from .views import company_list, company_detail, fetch_company_data
#--------api---------------
from .views import CompanyListAPIView, CompanyDetailView, CustomTokenObtainPairView, LoginView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .views import ProtectedView
# from rest_framework.authtoken.views import obtain_auth_token


#----------api_class------------


class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "authentication seccess welcome!"})

#---------api_class_end-----------------


urlpatterns = [
    path('companies/', company_list, name='company_list'),
    path('companies/<int:company_id>/print-weight-cards/', print_weight_cards, name='print_weight_cards'),
    path('companies/<int:company_id>/', company_detail, name='company_detail'),
    path('companies/<int:company_id>/fetch-data/', fetch_company_data, name='fetch_company_data'),
    #---------api------------
    path('api/companies/', CompanyListAPIView.as_view(), name='company-list'),  # عرض أو إضافة الشركات)(keep)
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),  # تفاصيل الشركة أو تعديلها أو حذفها)(keep)
    # path('api/login/', LoginView.as_view(), name='login'),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/protected/', ProtectedView.as_view(), name='protected-view'),
    #-------------api_end------------
]
