from django import forms
from .models import PatientMedicalUpload, Prescription

class PatientMedicalUploadForm(forms.ModelForm):
    class Meta:
        model = PatientMedicalUpload
        fields = ['patient', 'doctor', 'scanreport', 'reportdate']

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'doctor', 'prescription', 'dates']
