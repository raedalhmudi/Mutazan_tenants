from django.urls import path
from .views import company_list, company_detail, fetch_company_data

# -------------------------------------api------------------------
#--------api---------------
# from .views import CompanyListAPIView, CompanyDetailView, CustomTokenObtainPairView, LoginView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .views import ProtectedView
# -------------------------------------api------------------------

urlpatterns = [
    path('companies/', company_list, name='company_list'),
    path('companies/<int:company_id>/', company_detail, name='company_detail'),
    path('companies/<int:company_id>/fetch-data/', fetch_company_data, name='fetch_company_data'),
]
