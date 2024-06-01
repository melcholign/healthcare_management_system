from django.shortcuts import render
from django.db import connection
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime
from util.decorators import account_permission
from util.functions import dictfetchall, next_weekday_date, get_account_id
from accounts.views import configureNavBar
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import json
from pprint import pprint

# Create your views here.

# def configureNavBar(request, context):
#     for key, value in request.session.items():
#         print(f"Key: {key}, Value: {value}")
#     if isLoggedIn(request):
#         with connection.cursor() as cursor:
#             cursor.execute(f'''select first_name, last_name from auth_user where id = {value['account_id']}
#                                ''')
#             row = cursor.fetchone()
#             context['firstName'] = row[0]
#             context['lastName'] = row[1] 
#             context['account_type'] = value['account_type']
#             context["isLoggedIn"] = isLoggedIn(request)

def home(request):
    context = {}
    configureNavBar(request, context)
    return render(request, 'index.html', context)

@csrf_exempt
@account_permission('doctor')
def attend_appointment(request, appointment_id):
    
    context = {}
    
    if request.method == 'GET':
        
        with connection.cursor() as cursor:
            
            cursor.execute(f'''
                           SELECT patient.id AS id, CONCAT(first_name, " ", last_name) AS name, 
                            TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age, sex
                           FROM index_appointment AS appointment
                           JOIN accounts_patient AS patient ON appointment.patient_id = patient.id
                           JOIN auth_user as user ON patient.user_id = user.id
                           WHERE appointment.id = {appointment_id}
                           ''')
            patient_info = dictfetchall(cursor)[0]
            patient_info['sex'] = 'Male' if patient_info['sex'] == 'm' else 'Female'
            
            cursor.execute(f'''
                           SELECT doctor.id AS id, CONCAT("Dr. ", first_name, " ", last_name) AS name, specialty, 
                            department, qualification, workplace_id AS workplace, contact
                           FROM index_appointment AS appointment
                           JOIN accounts_availability AS availability ON appointment.doctor_schedule_id = availability.id
                           JOIN accounts_doctor AS doctor ON availability.doctor_id = doctor.id
                           JOIN accounts_institution AS institution ON institution.address = doctor.workplace_id
                           JOIN auth_user as user ON doctor.user_id = user.id
                           WHERE appointment.id = {appointment_id} 
                           ''')
            doctor_info = dictfetchall(cursor)[0]
            
            cursor.execute(f'''
                           SELECT diagnosis.id AS id, disease FROM index_diagnosis AS diagnosis
                           JOIN index_appointment AS appointment ON diagnosis.appointment_id = appointment.id
                           JOIN accounts_patient AS patient ON appointment.patient_id = patient.id
                           JOIN accounts_availability AS availability ON appointment.doctor_schedule_id = availability.id
                           JOIN accounts_doctor AS doctor ON availability.doctor_id = doctor.id
                           WHERE patient.id = {patient_info['id']} AND doctor.id = {doctor_info['id']} AND isValid = true
                           ''')
            previous_diagnoses = dictfetchall(cursor)
            
            cursor.execute(f'''
                           SELECT prescription.id AS id, medicine, dosage, timing, beforeMeal
                           FROM index_prescription AS prescription
                           JOIN index_appointment AS appointment ON prescription.appointment_id = appointment.id
                           JOIN accounts_patient AS patient ON appointment.patient_id = patient.id
                           JOIN accounts_availability AS availability ON appointment.doctor_schedule_id = availability.id
                           JOIN accounts_doctor AS doctor ON availability.doctor_id = doctor.id
                           WHERE patient.id = {patient_info['id']} AND doctor.id = {doctor_info['id']}
                           ''')
            previous_prescription = dictfetchall(cursor)
                        
            context.update({
                'patient_info': patient_info,
                'doctor_info': doctor_info,
                'previous_diagnoses': previous_diagnoses,
                'previous_prescription': previous_prescription,
            })
            
            return render(request, 'attend_appointment.html', context)
    
    if request.method == 'POST':
        
        post_data = json.loads(request.body)
            
        cured_diagnosis_ids = post_data['cured_diagnosis_ids']
        deleted_prescription_ids = post_data['deleted_prescription_ids']
        new_diagnoses = post_data['new_diagnoses']
        new_prescriptions = post_data['new_prescriptions']
        
        with connection.cursor() as cursor:
            for id in cured_diagnosis_ids:
                cursor.execute(f'UPDATE index_diagnosis SET isValid = false WHERE id = {id}')
            
            
            for id in deleted_prescription_ids:
                cursor.execute(f'DELETE FROM index_prescription WHERE id = {id}')
                
            for diagnosis in new_diagnoses:
                cursor.execute(f'''INSERT INTO index_diagnosis (appointment_id, disease, isValid)
                               SELECT {appointment_id}, "{diagnosis}", 1''')
                
            for prescription in new_prescriptions:
                cursor.execute(f'''INSERT INTO index_prescription (appointment_id, medicine, dosage, timing, beforeMeal)
                               SELECT {appointment_id}, "{prescription['medicine']}", {prescription['dosage']}, 
                               "{prescription['timing']}", {prescription['before_meal']}''')
        
        return HttpResponse(status=200)
    

@account_permission('doctor')
def prescribe(request, appointmentID):
    context = {}
    configureNavBar(request, context)
    doctor_id = 2
    
    if request.method == 'POST':
        post_data = request.POST
        medicine = post_data['medicine']
        dosage = post_data['dosage']
        timing = post_data['timing']
        before_meal = post_data['before_meal']
        
        with connection.cursor() as cursor:
            cursor.execute(f'''INSERT INTO index_prescription (appointment, medicine, dosage, timing, before_meal)
                           VALUES ({appointmentID}, "{medicine}", "{dosage}", "{timing}", {before_meal})
                           ''')
        
        return HttpResponseRedirect(reverse('doctor_appointment_list'))
    
    context['appointment_list'] = __fetch_doctor_appointment_list(doctor_id)
    
    return render(request, 'prescribe.html', context)

@account_permission('doctor')
def diagnosis(request, appointmentID):
    context = {}
    configureNavBar(request, context)
    doctor_id = 2
    
    if request.method == 'POST':
        post_data = request.POST
        disease = post_data['disease']
        symptoms = post_data['symptoms']
        isValid = post_data['isValid']
        
        with connection.cursor() as cursor:
            cursor.execute(f'''INSERT INTO index_diagnosis (appointment, disease, symptoms, isValid)
                           VALUES ({appointmentID}, "{disease}", "{symptoms}", "{isValid}")
                           ''')
        
        return HttpResponseRedirect(reverse('doctor_appointment_list'))
    
    context['appointment_list'] = __fetch_doctor_appointment_list(doctor_id)
    
    return render(request, 'diagnosis.html', context)


@account_permission('doctor')
def doctor_appointment_list(request):
    context = {}
    configureNavBar(request, context)
    doctor_id = get_account_id(request.session['account_data']['account_id'], 'doctor')

    if request.method == 'POST':
        post_data = request.POST
        
        date = post_data['date']
        start_time = post_data['start_time']
        
        with connection.cursor() as cursor:
            cursor.execute(f'''DELETE FROM index_appointment
                           WHERE date = "{date}" AND doctor_schedule_id in (
                               SELECT id FROM accounts_availability
                               WHERE doctor_id = {doctor_id} AND start_time = "{start_time}" 
                           )
                           ''')
        
        return HttpResponseRedirect(reverse('doctor_appointment_list'))
    
    context['appointment_list'] = __fetch_doctor_appointment_list(doctor_id)
    print(context['appointment_list'])
    
    return render(request, 'doctor_appointment_list.html', context)



@account_permission('patient')
def patient_appointment_list(request):
    """ 
    Generates a list of appointments made by a patient
    """
    context = {}
    configureNavBar(request, context)
    
    # Assuming that a logged-in patient account invoked this view
    account_data = request.session['account_data']
    patient_id = get_account_id(account_data['account_id'], account_data['account_type'])
    
    # handles rescheduling and deletion one at a time
    if request.method == 'POST':
        post_data = request.POST
        
        with connection.cursor() as cursor:
            # request to reschedule appointment
            if 'reschedule' in post_data:
                appointment_id = post_data['reschedule']
                
                # Get the week day of the date when an appointment had been set
                cursor.execute(f'''
                               SELECT work_day from accounts_availability AS ava
                               JOIN index_appointment AS app ON doctor_schedule_id = ava.id
                               WHERE app.id = {appointment_id}
                               ''')
                
                # Get the date of the upcoming week day
                date = next_weekday_date(cursor.fetchall()[0][0])
                
                
                cursor.execute(f'''
                               INSERT INTO index_appointment (doctor_schedule_id, patient_id, date, status)
                               SELECT doctor_schedule_id, patient_id, "{date}", "p"
                               FROM index_appointment
                               WHERE id = {appointment_id}   
                               ''')
                
            # request to cancel appointment
            else:
                appointment_id = post_data['cancel']
                
                # Delete appointment record using appointment_id
                cursor.execute(f'DELETE FROM index_appointment WHERE id={appointment_id}')
    
    # Update appointment statuses
    __update_appointments(patient_id)
    context['appointment_list'] = __fetch_patient_appointment_list(patient_id)
    pprint(context)
    return render(request, 'patient_appointment_list.html', context)


@account_permission('patient')
def make_appointment(request):
    """
    Provides the mechanisms by which valid appointments can be made
    """
    context = {}
    configureNavBar(request, context)
    # Assuming that a logged-in patient account invoked this view
    account_data = request.session['account_data']
    patient_id = get_account_id(account_data['account_id'], account_data['account_type'])
        
    if request.method == "POST":
        post_data = request.POST
                
        doctor_name = post_data['doctor_name']
        specialty = post_data['specialty']
        [schedule_id, date] = post_data['schedule'].split(', ')
        
        with connection.cursor() as cursor:
            
            # validation check: no time period for any appointments already made should not conflict
            # with that of the chosen appointment
            
            # Get start and end times of the appointment schedule
            cursor.execute(f'''SELECT start_time, end_time FROM accounts_availability WHERE id={schedule_id}''')
            start_time, end_time = dictfetchall(cursor)[0].values()
            
            # Get the name and specialty of the doctors, as well as the scheduled time and date of their pending
            # appointments with the patient that conflict with the schedule of the chosen appointment
            cursor.execute(f'''
                           SELECT CONCAT(first_name, " ", last_name) AS doctor_name, specialty, start_time, end_time, date
                           FROM accounts_availability AS ava
                           JOIN index_appointment AS app ON ava.id=app.doctor_schedule_id
                           JOIN accounts_doctor AS doc ON doc.id=ava.doctor_id
                           JOIN auth_user ON auth_user.id=doc.user_id
                           WHERE patient_id={patient_id} AND date="{date}"
                           AND (("{start_time}" < end_time AND "{start_time}" > start_time)
                           OR ("{end_time}" < end_time AND "{end_time}" > start_time))
                        ''')
            
            conflicting_schedules = dictfetchall(cursor)
            

            if conflicting_schedules:
                
                context.update({
                    'schedule_error': {
                        'chosen_schedule': {
                                'doctor_name': doctor_name,
                                'specialty': specialty,
                                'start_time': start_time,
                                'end_time': end_time,
                                'date': datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y'),
                            },
                        
                        'conflicting_schedule_list': conflicting_schedules,
                        },
                })
                
            else:
                cursor.execute(f'''INSERT INTO index_appointment(doctor_schedule_id, patient_id, date, status) 
                               VALUES ({schedule_id}, {patient_id}, "{date}", "p")''')
                return redirect("/")
                
   
    context['doctor_schedule_list'] = __fetch_doctor_schedule_list(patient_id)

    return render(request, 'make_appointment.html', context)

def __fetch_doctor_appointment_list(doctor_id):
    """
    Fetch a list of appointments corresponding to particular date
    sorted by date and time 
    """
    appointment_list = []
    with connection.cursor() as cursor:
        cursor.execute(f'''
                       SELECT date, start_time, end_time, app.id AS appointment_id, first_name, last_name
                       FROM index_appointment AS app
                       JOIN accounts_availability AS ava ON app.doctor_schedule_id = ava.id
                       JOIN accounts_patient AS acc ON app.patient_id = acc.id
                       JOIN auth_user AS user ON acc.user_id = user.id
                       WHERE doctor_id = {doctor_id} AND (date > CURDATE()
                       OR (date = CURDATE() AND start_time > CURTIME()))
                       ORDER BY date, start_time, appointment_id
                       ''')
        appointments = dictfetchall(cursor)
        
        print(appointments)
        
        for appointment in appointments:
            # if the list is empty or the date on the last entry is not equal to that on appointment,
            # add a new entry with the appointment date
            if len(appointment_list) == 0 or appointment_list[-1]['date'] != appointment['date']:
                appointment_list += [{
                    'total': 0,
                    'date': appointment['date']
                    }]
            
            recent = appointment_list[-1]
            
            if 'time_slot' not in recent:
                recent['time_slot'] = []
                        
            if len(recent['time_slot']) == 0 or recent['time_slot'][-1]['start_time'] != appointment['start_time']:
                recent['time_slot'] += [{
                    'start_time': appointment['start_time'],
                    'end_time': appointment['end_time'],
                    'appointments': [],
                    }]
            
            recent['time_slot'][-1]['appointments'] += [{
                'appointment_id': appointment['appointment_id'],
                'first_name': appointment['first_name'],
                'last_name': appointment['last_name'],
            }]
            
            recent['total'] += 1
            appointment_list[-1] = recent
                        
    return appointment_list

def __fetch_patient_appointment_list(patient_id):
    """
    Get the list of all appointments that a patient that a patient has pending, missed, and visited
    """
    with connection.cursor() as cursor:
        cursor.execute(f'''
                       SELECT app.id AS id, date, start_time, end_time, CONCAT(first_name, " ", last_name) AS doctor_name,
                       specialty, inst.name AS workplace, status
                       FROM index_appointment AS app
                       JOIN accounts_availability AS ava ON doctor_schedule_id=ava.id
                       JOIN accounts_doctor AS doc ON doctor_id=doc.id
                       JOIN accounts_institution as inst ON workplace_id=address
                       JOIN auth_user AS user ON user_id=user.id
                       WHERE patient_id={patient_id}
                       ORDER BY date, start_time
                       ''')
        return dictfetchall(cursor)
    
def __update_appointments(patient_id):
    """
    Update the status of a pending appointment to 'm' for 'missed'
    if its date or time has been passed
    """
    
    with connection.cursor() as cursor:
        cursor.execute(f'''
                    UPDATE index_appointment
                    SET status = "m"
                    WHERE patient_id = {patient_id} and status = 'p'
                    AND (date < CURDATE() OR (date = CURDATE() AND id in (
                        SELECT id FROM accounts_availability
                        WHERE id = doctor_schedule_id
                        AND end_time < CURTIME()
                    )))
                    ''')

def __fetch_doctor_schedule_list(patient_id):
    """
    Returns a list of doctors and their schedules that do not intersect with that
    an existing appointment made by the patient
    """
    doctor_schedule_list = []
    
    with connection.cursor() as cursor:
        # Get all available available doctors
        cursor.execute('''SELECT d.id AS id, first_name, last_name, specialty, i.name AS workplace
            FROM auth_user AS u, accounts_doctor AS d, accounts_institution AS i
            WHERE u.id=user_id and available=1 and d.workplace_id=i.address''')
        available_doctors = dictfetchall(cursor)
        
        for doctor in available_doctors:
            # For each available doctor, get their schedules except those that already 
            # share an appointment with the patient
            cursor.execute(f'''
                SELECT ava.id AS schedule_id, work_day, start_time, end_time
                FROM accounts_availability AS ava
                WHERE doctor_id={doctor['id']} and deleted=0
                EXCEPT
                SELECT ava.id AS schedule_id, work_day, start_time, end_time 
                FROM accounts_availability as ava JOIN index_appointment ON doctor_schedule_id=ava.id
                WHERE patient_id={patient_id} AND status='p'
            ''')
            
            doctor_schedule_list += [{
                    'doctor': doctor,
                    'schedules': dictfetchall(cursor)
                }]
            
            # for each work day in the doctor's schedule, get the corresponding date that falls within a week
            # from the today
            for schedule in doctor_schedule_list[-1]['schedules']:
                schedule['date'] = next_weekday_date(schedule['work_day'])
            
    return doctor_schedule_list
