from django.shortcuts import render,redirect
from .models import Patient, MedicalRecord, Report,Department,Doctor,Booking,BloodTest,Medicalrepotupload,BloodTestReport
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#doctors import file
from .forms import DoctorForm
from .models import Prediction
from .forms import BookingForm
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
# Create your views here.
def index(req):
    return render(req,'index.html')

#patient
def add_patient(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']

        # Save the patient details
        patient = Patient(name=name, email=email, password=password, phone=phone)
        patient.save()

        return redirect('/login/')  # Replace 'success_page' with your success URL
    return render(request, 'patient/patient_form.html')

def success(req):
    return render(req,'successpage.html')

def register_medical(request):
    if request.method == 'POST':
        patient_id = request.POST['patient']
        diagnosis = request.POST['diagnosis']
        treatment = request.POST['treatment']

        # Create the medical record
        patient = Patient.objects.get(id=patient_id)
        medical_record = MedicalRecord.objects.create(
            patient=patient,
            diagnosis=diagnosis,
            treatment=treatment
        )

        # Handle multiple file uploads
        for file in request.FILES.getlist('reports'):
            Report.objects.create(medical_record=medical_record, file=file)

        return redirect('dashboard/')  # Replace with your success page URL
    else:
        patients = Patient.objects.all()
        return render(request, 'patient/medical_register_form.html', {'patients': patients})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate the user
        user = Patient.objects.filter(email=email,password=password).first()
        if user is not None:
             
            request.session['user_name'] = user.name  # Save custom data in the session
            request.session['userid']=user.id
            return redirect('/dashboard/')  # Redirect to a dashboard or home page
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'patient/login.html')


def dashboard_view(request):
    user_name = request.session.get('user_name', 'Guest')  # Retrieve custom session data
    userid=request.session.get('userid')
    return render(request, 'patient/dashboard.html', {'user_name': user_name,'userid':userid})

def logout_view(request):
    logout(request)  # Clear the session and log the user out
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')  # Redirect to the login page    
def patient_list(request):
    # Retrieve all patients from the database
    patients = Patient.objects.all()
    return render(request, 'patient/patient_list.html', {'patients': patients})

def doctor_register(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor registered successfully!')
            return redirect('doctor_register')  # Update with the desired redirect URL
    else:
        form = DoctorForm()
    return render(request, 'doctor/doctor_register.html', {'form': form})


def doctor_login(request):
    error_message = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try to authenticate the doctor
        if email and password:
            doctor =Doctor.objects.filter(email=email, password=password).first()
            if doctor is not None:
                request.session['doctorid']=doctor.id
                request.session['doctor_name']=doctor.name
                patient=Booking.objects.select_related('patient', 'doctor').filter(doctor=doctor)
                return render(request, 'doctor/doctor_dashboard.html', {'doctor': doctor,'bookings':patient})
            else:
                error_message = "Invalid email or password"

    return render(request, 'doctor/doctor_login.html', {'error_message': error_message})

#perdicition
# Load datasets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
symptoms_data = pd.read_csv(os.path.join(BASE_DIR, 'C:/collegeproject/healthai-main/dataset/Training.csv.zip'))
department_data = pd.read_csv(os.path.join(BASE_DIR, 'C:/collegeproject/healthai-main/dataset/Doctor_Versus_Disease.csv'), encoding='latin1')

# Preprocess the symptoms dataset
X = symptoms_data.drop(['prognosis', 'Unnamed: 133'], axis=1)
y = symptoms_data['prognosis']

# Encode the target labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train a model
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Symptoms list
symptoms = list(X.columns)

def predict(request):
    
    if request.method == "POST":
        # Collect form data
        
        patient_name = request.POST.get('patient_name')
        selected_symptoms = {symptom: int(request.POST.get(symptom, 0)) for symptom in symptoms}

        # Ensure at least one symptom is selected
        if sum(selected_symptoms.values()) == 0:
            return render(request, 'predict.html', {
                'symptoms': symptoms,
                'error': "Please select at least one symptom."
            })

        # Convert symptoms to DataFrame
        input_data = pd.DataFrame([selected_symptoms])

        # Predict the disease
        prediction = model.predict(input_data)
        predicted_disease = label_encoder.inverse_transform(prediction)[0]

        # Fetch the department dynamically
        department_row = department_data[department_data['Drug Reaction'] == predicted_disease]
        department = department_row.iloc[0]['Allergist'] if not department_row.empty else "Unknown Department"

        # Save prediction to the database
        Prediction.objects.create(
            patient_name=patient_name,
            predicted_disease=predicted_disease,
            department=department,
            symptoms_selected=", ".join([symptom for symptom, value in selected_symptoms.items() if value == 1])
        )

        # Fetch the department object
        departments = Department.objects.filter(name=department).first()
                
        # Fetch doctors associated with the department
        doctor = Doctor.objects.filter(department=departments.id) if departments else None
        # if doctor:
        #   print(doctor.name)
        # else:
        #     None  

        # Pass results to the template
        return render(request, 'result.html', {
            'patient_name': patient_name,
            'predicted_disease': predicted_disease,
            'department': department,
            'doctor': doctor  # Corrected the key
        })

    return render(request, 'predict.html', {'symptoms': symptoms,'username':request.session.get('user_name', 'Guest')})
def doctorpredict(request):
    
    if request.method == "POST":
        # Collect form data
        
        patient_name = request.POST.get('patient_name')
        selected_symptoms = {symptom: int(request.POST.get(symptom, 0)) for symptom in symptoms}

        # Ensure at least one symptom is selected
        if sum(selected_symptoms.values()) == 0:
            return render(request, 'predict.html', {
                'symptoms': symptoms,
                'error': "Please select at least one symptom."
            })

        # Convert symptoms to DataFrame
        input_data = pd.DataFrame([selected_symptoms])

        # Predict the disease
        prediction = model.predict(input_data)
        predicted_disease = label_encoder.inverse_transform(prediction)[0]

        # Fetch the department dynamically
        department_row = department_data[department_data['Drug Reaction'] == predicted_disease]
        department = department_row.iloc[0]['Allergist'] if not department_row.empty else "Unknown Department"

        # Save prediction to the database
        Prediction.objects.create(
            patient_name=patient_name,
            predicted_disease=predicted_disease,
            department=department,
            symptoms_selected=", ".join([symptom for symptom, value in selected_symptoms.items() if value == 1])
        )

        # Fetch the department object
        departments = Department.objects.filter(name=department).first()
                
        # Fetch doctors associated with the department
        doctor = Doctor.objects.filter(department=departments.id) if departments else None
        # if doctor:
        #   print(doctor.name)
        # else:
        #     None  
        search_query = f"{predicted_disease} treatment"
        treatment_details = search_medicine_treatment(search_query)  
        # Pass results to the template
        return render(request, 'doctor/result.html', {
            'patient_name': patient_name,
            'predicted_disease': predicted_disease,
            'department': department,
            "treatment_details":treatment_details,
            'doctor': doctor,  # Corrected the key
            
        })

    return render(request, 'doctor/doctorpredict.html', {'symptoms': symptoms,'username':request.session.get('user_name', 'Guest')})




def search_medicine_treatment(query):
    # Google search URL
    google_search_url = f"https://www.google.com/search?q={query}+medicine+treatment"
    
    # Set user-agent to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Make the request to Google
    response = requests.get(google_search_url, headers=headers)
    
    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract search result snippets
    results = []
    for g in soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd"):
        if g.text:
            results.append(g.text)

    # Return the top 5 results
    return results[:5]  # Limit to top 5 results

#booking
def book_appointment(request):
    predict=request.GET.get('predict')
    doctor_id=request.GET.get('drid')
    print(doctor_id)
    print(predict)
    doctor=Doctor.objects.filter(id=doctor_id)
    
    print(doctor)
    if request.method=="POST":
        doctorobj=Doctor.objects.get(id=request.POST.get('drid'))
        Booking.objects.create(
            patient=Patient.objects.get(id=request.session.get('userid')),
            doctor=doctorobj,
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            symptoms=request.POST.get('predict')
        )
        return render(request,'successpage.html')
       
    return render(request, 'book_appointment.html', {"doctors":doctor,"predict":predict})


def register_blood_test(request):
    if request.method == 'POST':
        # Get the patient, doctor, and test data from the POST request
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        test_names = request.POST.getlist('test_names')  # Multiple tests

        # Retrieve the Patient and Doctor instances
        patient = Patient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)

        # Create and save the new BloodTest instance
        blood_test = BloodTest.objects.create(
            patient=patient,
            doctor=doctor,
            test_names=test_names
        )
        patients = Patient.objects.all()
        doctors = Doctor.objects.all()

        # Redirect to a success page after saving
        return render(request, 'doctor/bloodtest.html', {'patients': patients, 'doctors': doctors,'message':"register success"})  # Update 'success' with the actual URL for your success page

    else:
        # Retrieve the list of patients and doctors to display in the select fields
        patients = Patient.objects.all()
        doctors = Doctor.objects.all()

    return render(request, 'doctor/bloodtest.html', {'patients': patients, 'doctors': doctors,'message':''})


def viewBloodResult(request):
    if request.method=="GET":
        patientid=request.GET.get('patientid')
        patient_id=Patient.objects.get(id=patientid)
        result=BloodTestReport.objects.select_related('doctor','patient').filter(patient=patient_id)
        return render(request,'doctor/bloodresult.html',{"results":result})
    

from .models import  Prescription



def add_prescription(request):
    
    doctorid=request.session.get('doctorid')
    patientid=request.GET.get('patientid')
    print(patientid)
    doctor=Doctor.objects.get(id=doctorid)
    patient=Patient.objects.get(id=patientid)
    if request.method=="POST":
        Prescription.objects.create(
            prescription=request.POST.get('prescription'),
            doctor=doctor,
            patient=patient
        )
        print("add prescription")
        return render(request, 'doctor/add_prescription.html', {patient:patient,"message":"success"})      
    return render(request, 'doctor/add_prescription.html', {"patient":patientid,"message":""})

def viewprescription(request):
    if request.method=="GET":
        patientid=request.GET.get('patientid')
        patient=Prescription.objects.select_related('doctor','patient').filter(patient=Patient.objects.get(id=patientid))
        return render(request,'patient/viewpresription.html',{'patient':patient})
    patientid=request.session.get('userid')
    patient=Prescription.objects.select_related('doctor','patient').filter(patient=Patient.objects.get(id=patientid))
    return render(request,'patient/viewprescription.html',{'patient':patient})

def upload_medical_report(request):
    # Check if the request is a POST
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        uploadfile = request.FILES.get('uploadfile')

        # Validate data
        if patient_id and doctor_id and uploadfile:
            try:
                # Get the patient and doctor objects
                patient = Patient.objects.get(id=patient_id)
                doctor = Doctor.objects.get(id=doctor_id)

                # Create a new Medicalreportupload object and save it
                medical_report = Medicalrepotupload(
                    patient=patient,
                    doctor=doctor,
                    uploadfile=uploadfile
                )
                medical_report.save()

                patients = Patient.objects.all()
                doctors = Doctor.objects.all()

                context = {
                        'patients': patients,
                        'doctors': doctors,
                        'message':'Report Add Successfully'
                    }
                return render(request, 'patient/add_medical_report.html', context)  # Redirect to a success page or reload
            except (Patient.DoesNotExist, Doctor.DoesNotExist):
                return HttpResponse("Invalid Patient or Doctor ID.")
        else:
            return HttpResponse("All fields are required.")
    
    # For GET requests, send the form with data
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()

    context = {
        'patients': patients,
        'doctors': doctors,
        "message":'',
    }
    return render(request, 'patient/add_medical_report.html', context)

def medical_report_list(request):
    # Fetch all medical reports from the database
    reports = Medicalrepotupload.objects.all()

    # Pass the reports to the template
    context = {
        'reports': reports
    }
    print(reports)
    return render(request, 'doctor/medical_report_list.html', context)

