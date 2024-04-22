from django.db import models
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
