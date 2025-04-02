# في urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    # روابط التطبيقات الأخرى
]

# إضافة إعدادات الوسائط إذا كنت في بيئة التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
