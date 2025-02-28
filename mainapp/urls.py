from django.urls import path
from . import views
urlpatterns = [
    path("",views.index),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('successpage/',views.success),
    path('register_medical/',views.register_medical),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('patients/', views.patient_list, name='patient_list'),
    path('doctor/register/', views.doctor_register, name='doctor_register'),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('predict/', views.predict, name='predict'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('blood_test/',views.register_blood_test,name='register_blood_test'),
    path('add_prescription/',views.add_prescription,name="add_prescription"),
    path('view_prescription/',views.viewprescription,name="viewprescription"),
    path('add_medical_report/',views.upload_medical_report,name="upload_medical_report"),
    path('medical-reports/', views.medical_report_list, name='medical_report_list'),
    path('doctorpredict/',views.doctorpredict,name="doctorpredict"),
    path('bloodresult/',views.BloodTestReport,name="BloodTestReport")

]
