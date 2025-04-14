from django.urls import path
from .views import company_list, company_detail, fetch_company_data, print_weight_cards

urlpatterns = [
    path('companies/', company_list, name='company_list'),
    path('companies/<int:company_id>/print-weight-cards/', print_weight_cards, name='print_weight_cards'),
    path('companies/<int:company_id>/', company_detail, name='company_detail'),
    path('companies/<int:company_id>/fetch-data/', fetch_company_data, name='fetch_company_data'),
]
