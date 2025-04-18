from django.urls import path
from . import views
from django.contrib import admin
# from .views import check_camera_connection
#---------api----------
from django.urls import path
from .views import InvoiceListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:pk>/print/', views.invoice_print_modal, name='invoice_print_modal'),
    # path('companies/', views.company_list, name='company_list'),
    # path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    # path('check_camera/<int:device_id>/', check_camera_connection, name='check_camera_connection'),
    # path('admin/dashboard/', views.admin_dashboard, name="admin_dashboard"),
    # path('video_feed/<str:camera_type>/', views.camera_feed, name='video_feed'),
    path('video_feed/<str:location>/', views.video_feed, name='video_feed'),
   #-----------api-----------
    path('api/invoices/', InvoiceListView.as_view(), name='invoice-list'),
    # مسارات أخرى...
]
