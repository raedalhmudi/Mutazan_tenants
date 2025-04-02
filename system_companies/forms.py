# from django import forms
# from .models import Devices
# from .admin import *

# class DevicesForm(forms.ModelForm):
#     class Meta:
#         model = Devices
#         fields = '__all__'  # أو تحديد الحقول التي تريد عرضها

# @admin.register(Devices)
# class DevicesAdmin(admin.ModelAdmin):
#     form = DevicesForm
#     list_display = ['name_devices', 'address_ip', 'connection_type', 'device_status', 'location']
