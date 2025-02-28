from django.contrib import admin
from .models import Department,Patient,Doctor,BloodTest,Medicalrepotupload,BloodTestReport
# Register your models here.
from .models import Prediction,Booking

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'predicted_disease', 'department', 'date_created')
    list_filter = ('date_created', 'department')

admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Booking)
admin.site.register(BloodTest)
admin.site.register(Medicalrepotupload)
admin.site.register(BloodTestReport)