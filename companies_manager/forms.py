from django import forms
from django.utils.safestring import mark_safe
from .models import Company

class CompanyAdminForm(forms.ModelForm):
    logo = forms.ImageField(
        label="شعار الشركة",
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',  # بدون class
        })
    )


    class Meta:
        model = Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.logo:
            self.fields['logo'].help_text = mark_safe(
                f'<img src="{self.instance.logo.url}" style="max-height: 100px; margin-top: 10px;" />'
            )
