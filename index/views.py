from django.shortcuts import render
import datetime
from accounts.models import Doctor, Patient
from .models import Appointment
from django.db import connection
from django.contrib.auth.models import User
from util import dictfetchall

# Create your views here.
def home(request):
    return render(request, 'index.html')


def makeAppointment(request):
    cursor = connection.cursor()
    if request.method == "POST":
        doctorID = request.POST['doctor']
        doctorQuery = "SELECT * FROM accounts_doctor WHERE id = %s"
        cursor.execute(doctorQuery, [doctorID])

        patientID = request.user.id
        patientQuery = "SELECT * FROM accounts_patient WHERE user_id = %s"
        cursor.execute(patientQuery, [patientID])

        date = datetime.datetime.now().strftime('%Y-%m-%d')
        time = datetime.datetime.now().strftime('%H:%M:%S')

        insertQuery = "INSERT INTO index_appointment(doctor_id, patient_id, date, time) VALUES (%s, %s, %s, %s)"
        cursor.execute(insertQuery, [doctorID, patientID, date, time])

    return render(request, 'makeAppointment.html')

def __fetch_doctor_schedules(patient_id):
    doctor_schedules = []
    
    with connection.cursor() as cursor:
        cursor.execute('''SELECT d.id AS id, first_name, last_name, specialty, i.name AS workplace
            FROM auth_user AS u, accounts_doctor AS d, accounts_institution AS i
            WHERE u.id=user_id and available=1 and d.workplace_id=i.address''')
        available_doctors = dictfetchall(cursor)
        
        for doctor in available_doctors:
            cursor.execute(f'''
                (SELECT work_day, start_time, end_time
                FROM accounts_availability
                WHERE doctor_id={doctor['id']})
                EXCEPT
                (SELECT work_day, start_time, end_time 
                FROM accounts_availability as ava, index_appointment
                WHERE doctor_id={doctor['id']} and doctor_schedule_id=ava.id and patient_id={patient_id})
            ''')
            
            doctor_schedules += [{
                    'doctor': doctor,
                    'schedules': dictfetchall(cursor)
                }]
            
    return doctor_schedules
