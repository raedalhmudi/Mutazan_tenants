from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(label="رقم الهاتف", required=False)
    address = forms.CharField(label="عنوان السكن", widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(label="صورة المستخدم", required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "phone_number", "address", "profile_picture")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                profile_picture=self.cleaned_data['profile_picture'],
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address']
            )
        return user