from rest_framework import serializers
from .models import Invoice  # تأكد من اسم الموديل

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [ 'id', 'weight_card', 'material', 'quantity', 'datetime', 'net_weight']
# 