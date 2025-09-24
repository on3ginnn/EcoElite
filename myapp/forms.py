from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date

from .models import ServiceAddress, ServiceOrder


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    
    class Meta:
        model = User
        fields = ['email', 'phone', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username

class AddressForm(forms.ModelForm):
    class Meta:
        model = ServiceAddress
        fields = ['address', 'notes']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
        labels = {
            'address': 'Адрес обслуживания',
            'notes': 'Дополнительные указания',
        }

class OrderForm(forms.ModelForm):
    def __init__(self, client_profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = client_profile.addresses.all()
    
    class Meta:
        model = ServiceOrder
        fields = ['address', 'service_date', 'service_time', 'notes']
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'service_time': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'address': 'Адрес обслуживания',
            'service_date': 'Дата',
            'service_time': 'Время',
            'notes': 'Особые пожелания',
        }
    
    def clean_service_date(self):
        service_date = self.cleaned_data.get('service_date')
        if service_date and service_date < date.today():
            raise ValidationError('Нельзя выбрать прошедшую дату')
        return service_date