from django import forms
from .models import Doctor

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'register_no', 'email', 'phone', 'photo', 'department', 'booking_slot_days', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'register_no': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'booking_slot_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['doctor', 'date', 'time', 'symptoms']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
        }