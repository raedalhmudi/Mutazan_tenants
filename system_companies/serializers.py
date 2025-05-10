from rest_framework import serializers
from .models import Invoice  # تأكد من اسم الموديل
from .models import ViolationRecord

class ViolationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViolationRecord
        fields = ['id', 'type', 'description', 'created_at']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [ 'id', 'weight_card', 'material', 'quantity', 'datetime', 'net_weight']
# 