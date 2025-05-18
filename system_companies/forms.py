from django import forms
from .models import WeightCard

class WeightCardForm(forms.ModelForm):
    class Meta:
        model = WeightCard
        fields = '__all__'

    material = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text="أدخل المواد والكميات بصيغة JSON مثل: [{'material_id': 1, 'material_name': 'حديد', 'quantity': 5}]",
        required=False
    )

    def clean_material(self):
        import json
        raw = self.cleaned_data['material']
        try:
            parsed = json.loads(raw)
            for item in parsed:
                if 'material_id' not in item or 'quantity' not in item:
                    raise forms.ValidationError("كل عنصر يجب أن يحتوي على 'material_id' و 'quantity'")
            return parsed
        except Exception as e:
            raise forms.ValidationError("البيانات غير صالحة: " + str(e))
