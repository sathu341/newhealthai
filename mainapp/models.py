from django.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here.
class Patient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name
class MedicalRecord(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='medical_records')
    diagnosis = models.TextField()
    treatment = models.TextField()

    def __str__(self):
        return f"Medical Record for {self.patient.name}"

class Report(models.Model):
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='uploaded_reports'  # Use a unique related_name
    )
    file = models.FileField(upload_to='reports/')

    def __str__(self):
        return f"Report for {self.medical_record.patient.name}"


#Doctor 
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    register_no = models.CharField(max_length=50, unique=True)  # Registration number
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    booking_slot_days = models.IntegerField()  # Number of days for booking slots
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"Dr. {self.name} ({self.department.name})" 

class Prediction(models.Model):
    patient_name = models.CharField(max_length=100)
    predicted_disease = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    symptoms_selected = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.predicted_disease}"   

class Booking(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bookings')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    time = models.TimeField()
    symptoms = models.TextField()

    def __str__(self):
        return f"Booking by {self.patient.name} with Dr. {self.doctor.name} on {self.date} at {self.time}"     
    
#LAb
class BloodTest(models.Model):
    TEST_CHOICES = [
        ('CBC', 'Complete Blood Count (CBC)'),
        ('LFT', 'Liver Function Test (LFT)'),
        ('RFT', 'Renal Function Test (RFT)'),
        ('Lipid', 'Lipid Profile'),
        ('Glucose', 'Blood Glucose Test'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='blood_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='blood_tests')
    test_names = models.JSONField(default=list)  # JSONField for array-like storage
    result_date=models.DateField(auto_now=True)

    def __str__(self):
        return f"Blood Tests for {self.patient.name} by Dr. {self.doctor.name}: {', '.join(self.test_names)}"  
class BloodTestReport(models.Model):
    testresult=models.FileField(upload_to='test_report/',blank=True,null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_blood_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_blood_tests')
    test_names = models.JSONField(default=list) 
    result_date=models.DateField(auto_now=True)
    def __str__(self):
        return f"Blood Tests for {self.patient.name} by Dr. {self.doctor.name}: {', '.join(self.test_names)}"  

    


class PatientMedicalUpload(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_reports')
    scanreport = models.ImageField(upload_to='patient_report/', blank=True, null=True)
    reportdate = models.DateField(auto_now=True)

    def __str__(self):
        return f"Upload Report of {self.patient.name} by Dr. {self.doctor.name}"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_prescriptions')
    prescription = models.TextField(max_length=100)
    dates = models.DateField(auto_now=True)

    def __str__(self):
        return f"Prescription For Patient: {self.patient.name} By Dr. {self.doctor.name}"

class Medicalrepotupload(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_report')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_report')
    uploadfile = models.FileField(upload_to='medical_report/', blank=True, null=True)
    dates = models.DateField(auto_now=True)

    def __str__(self):
        return f"Prescription For Patient: {self.patient.name} By Dr. {self.doctor.name}"

