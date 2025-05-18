from django.urls import path
from . import views
from django.contrib import admin
# from .views import check_camera_connection
#---------api----------
# from django.urls import path
# from .views import InvoiceListView

urlpatterns = [
    # path("admin/reports/", admin.site.admin_view(views.reports_view), name="admin-reports"),
    path('admin/', admin.site.urls),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:pk>/print/', views.invoice_print_modal, name='invoice_print_modal'),
    path('video_feed/<str:location>/', views.video_feed, name='video_feed'),
    path('print_report/', views.print_report, name='print_report'),
    path('logout/', views.logout_view, name='logout'),
    path('logout_complete/', views.logout_complete, name='logout_complete'),
   #-----------api-----------
    # path('api/invoices/', InvoiceListView.as_view(), name='invoice-list'),


    # مسارات أخرى...
]
