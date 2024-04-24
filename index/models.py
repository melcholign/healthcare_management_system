from django.db import models
from accounts.models import *


# Create your models here.

class Appointment(models.Model):
    doctor_schedule = models.ForeignKey(Availability, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    visited_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return (str(self.doctor_schedule.doctor) + " - " + str(self.patient) + " - " + str(self.date) 
                + " - " + str(self.doctor_schedule.start_time) + " - " + str(self.doctor_schedule.end_time))

class Disposals(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    disease = models.TextField()
    prescription = models.TextField()

