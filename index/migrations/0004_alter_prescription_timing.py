# Generated by Django 5.0.4 on 2024-06-01 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_diagnosis_prescription_delete_disposals'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prescription',
            name='timing',
            field=models.CharField(choices=[('morning', 'Morning'), ('noon', 'Noon'), ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('night', 'Night'), ('midnight', 'Midnight')], max_length=10),
        ),
    ]
