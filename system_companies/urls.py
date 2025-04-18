from django.urls import path
from . import views
from django.contrib import admin
# from .views import check_camera_connection
#---------api----------
# from django.urls import path
# from .views import InvoiceListView

urlpatterns = [
    path("admin/reports/", admin.site.admin_view(views.reports_view), name="admin-reports"),
    path('admin/', admin.site.urls),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:pk>/print/', views.invoice_print_modal, name='invoice_print_modal'),
    path('video_feed/<str:location>/', views.video_feed, name='video_feed'),
   #-----------api-----------
    # path('api/invoices/', InvoiceListView.as_view(), name='invoice-list'),


    # مسارات أخرى...
]
