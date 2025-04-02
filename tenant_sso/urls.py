from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_sso, name='initiate_sso'),
    path('validate/', views.validate_sso, name='validate_sso'),
]