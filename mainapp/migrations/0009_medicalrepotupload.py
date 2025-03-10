# Generated by Django 4.1 on 2025-01-22 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mainapp", "0008_prescription_patientmedicalupload"),
    ]

    operations = [
        migrations.CreateModel(
            name="Medicalrepotupload",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uploadfile",
                    models.FileField(
                        blank=True, null=True, upload_to="medical_report/"
                    ),
                ),
                ("dates", models.DateField(auto_now=True)),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="doctor_report",
                        to="mainapp.doctor",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="patient_report",
                        to="mainapp.patient",
                    ),
                ),
            ],
        ),
    ]
