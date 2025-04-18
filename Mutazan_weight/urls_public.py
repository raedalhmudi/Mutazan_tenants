"""
URL configuration for Mutazan_weight project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from companies_manager.admin import tenant_admin_site
from companies_manager.views import *
from django.conf.urls.i18n import set_language
#-------------توكن---------------
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from companies_manager.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenVerifyView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_tenants/', tenant_admin_site.urls),
    # path('', include('admin_adminlte.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('companies_manager.urls')),
    # path('users', include('user_management.urls')),
    path('set_language/', set_language, name='set_language'),
    #-----------مسارات التوكن و الapi--------------------
    path('api/', include('companies_manager.urls')),  # تأكد من أن المسارات الخاصة بالـ API موجودة في ملف `urls.py` الخاص بالشركات
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'), #هذا المسار يستخدم للتحقق مما إذا كان الـ access token صالحًا أو لا.
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), #صفحه تسجيل الدخول
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),#عندما ينتهي صلاحية access token (الذي يكون عادة لمدة قصيرة)، يمكن استخدام refresh token للحصول على access token جديد.
    path('', include('system_companies.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






# from django.contrib import admin
# from django.urls import path, include
# from django.conf.urls.static import static
# from django.conf import settings
# from companies_manager.admin import tenant_admin_site
# from companies_manager.views import *
# from django.conf.urls.i18n import set_language

# urlpatterns = [
#     path('master-admin/', admin.site.urls),  # تغيير المسار للإدارة الرئيسية
#     path('tenant-admin/', tenant_admin_site.urls),  # مسار إدارة المستأجرين
#     path('accounts/', include('allauth.urls')),
#     path('', include('companies_manager.urls')),
#     path('set_language/', set_language, name='set_language'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

