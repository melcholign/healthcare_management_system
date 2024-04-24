from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.contrib.auth.models import User

# Create your models here.
class Doctor(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    id = models.AutoField(primary_key=True)
    specialty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    qualification = models.TextField()
    workplace = models.ForeignKey('Institution', on_delete=models.RESTRICT)
    contact = models.BigIntegerField()  # A ten digit number for mobile number
    available = models.BooleanField(default=True)   # whether or not a doctor is available to accept patients

    def __str__(self):
        return "Dr. " + self.user.last_name + " - " + self.specialty


class Patient(models.Model):
    SEXES = (('m', 'male'), ('f', 'female'))
    
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    id = models.AutoField(primary_key=True)
    date_of_birth = models.DateField()
    date_of_death = models.DateField(null=True, blank=True)
    sex = models.CharField(null=True, choices=SEXES, max_length=1)  # Male or Female
    address = models.CharField(max_length=200)
    contact = models.BigIntegerField()  # A ten digit number for mobile number

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
    
class Institution(models.Model):
    """Represents a medical/healthcare institution that employs doctors"""
    name = models.CharField(max_length=100)
    address = models.CharField(primary_key=True, max_length=200)
    
    def __str__(self):
        return self.name
    
class Availability(models.Model):
    """Represents the time when a doctor is available to accept patients"""
    DAYS = (
        ('sun', 'Sunday'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday')
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    work_day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'work_day', 'start_time', 'end_time'],
                                    violation_error_message='A doctor must be available at any unique time and day',
                                    name='unique_availability'),
            models.CheckConstraint(check=Q(start_time__lt=F('end_time')),
                                   violation_error_message='Start time of availability must be less than its end time',
                                   name='check_availability_time'),
        ]
        
    def __str__(self):
        return self.doctor.__str__() + " - " + str(self.start_time) + " - " + str(self.end_time) + " - " + self.work_day