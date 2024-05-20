# Generated by Django 5.0.4 on 2024-05-20 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='availability',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='availability',
            constraint=models.UniqueConstraint(fields=('doctor', 'work_day', 'start_time', 'end_time'), name='unique_availability', violation_error_message='A doctor must be available at any unique time and day'),
        ),
        migrations.AddConstraint(
            model_name='availability',
            constraint=models.CheckConstraint(check=models.Q(('start_time__lt', models.F('end_time'))), name='check_availability_time', violation_error_message='Start time of availability must be less than its end time'),
        ),
    ]
