from django.db import models
from accounts.models import *


# Create your models here.

class Appointment(models.Model):
    STATUS = (
        ('p', 'pending'),
        ('v', 'visited'),
        ('m', 'missed'),
    )
    
    doctor_schedule = models.ForeignKey(Availability, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    visited_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default='p')

    def __str__(self):
        return (str(self.doctor_schedule.doctor) + " - " + str(self.patient) + " - " + str(self.date) 
                + " - " + str(self.doctor_schedule.start_time) + " - " + str(self.doctor_schedule.end_time))
    

class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medicine = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    timing = models.TimeField()
    beforeMeal = models.BooleanField(default=True)

class Diagnosis(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    disease = models.CharField(max_length=100)
    symptoms = models.CharField(max_length=1000)
    isValid = models.BooleanField(default=True)

# prescription table -- appt id, meds, dosage, timing of day, before/after food
# diagnosis -- appt id, disease name, isvalid 
# disposal -- array of dicts, 
