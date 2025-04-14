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
from system_companies import views
from django.conf.urls.i18n import set_language

urlpatterns = [
    path("admin/reports/", admin.site.admin_view(views.reports_view), name="admin-reports"),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    # path('', include('admin_adminlte.urls')),
    path('', include('system_companies.urls')),
    # path('users', include('user_management.urls')),
    path('set_language/', set_language, name='set_language'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







# from django.contrib import admin
# from django.urls import path, include
# from django.conf.urls.static import static
# from django.conf import settings
# from system_companies.views import *
# from django.conf.urls.i18n import set_language

# urlpatterns = [
#     path('system-admin/', admin.site.urls),  # تغيير المسار
#     path('accounts/', include('allauth.urls')),
#     path('', include('system_companies.urls')),
#     path('set_language/', set_language, name='set_language'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)