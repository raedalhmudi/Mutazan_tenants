from rest_framework import serializers
from companies_manager.models import Company
from .models import ViolationsType

class ViolationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViolationsType
        fields = ['id', 'name','description']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'  # تحديد الحقول التي سيتم تضمينها في الـ API