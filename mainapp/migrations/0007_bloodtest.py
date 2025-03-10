# Generated by Django 4.1 on 2025-01-21 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mainapp", "0006_booking"),
    ]

    operations = [
        migrations.CreateModel(
            name="BloodTest",
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
                ("test_names", models.JSONField(default=list)),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="blood_tests",
                        to="mainapp.doctor",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="blood_tests",
                        to="mainapp.patient",
                    ),
                ),
            ],
        ),
    ]
