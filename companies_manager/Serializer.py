from rest_framework import serializers
from companies_manager.models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'  # تحديد الحقول التي سيتم تضمينها في الـ API