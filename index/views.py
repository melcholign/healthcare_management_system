from django.shortcuts import render
from django.db import connection
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from util.decorators import account_permission
from util.functions import dictfetchall, next_weekday_date, get_account_id
from accounts.views import isLoggedIn

# Create your views here.
def configureNavBar(request, context):
    for key, value in request.session.items():
        print(f"Key: {key}, Value: {value}")
    if isLoggedIn(request):
        with connection.cursor() as cursor:
            cursor.execute(f'''select first_name, last_name from auth_user where id = {value['account_id']}
                               ''')
            row = cursor.fetchone()
            context['firstName'] = row[0]
            context['lastName'] = row[1] 
            context['account_type'] = value['account_type']
            context["isLoggedIn"] = isLoggedIn(request)

def home(request):
    context = {}
    configureNavBar(request, context)
    return render(request, 'index.html', context)

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
    doctor_id = 2
    
    if request.method == 'POST':
        post_data = request.POST
        
        date = post_data['date']
        start_time = post_data['start_time']
    
        print(date)
        print(start_time)
        
        with connection.cursor() as cursor:
            cursor.execute(f'''DELETE FROM index_appointment
                           WHERE date = "{date}" AND doctor_schedule_id in (
                               SELECT id FROM accounts_availability
                               WHERE doctor_id = {doctor_id} AND start_time = "{start_time}"
                           )
                           ''')
        
        return HttpResponseRedirect(reverse('doctor_appointment_list'))
    
    context['appointment_list'] = __fetch_doctor_appointment_list(doctor_id)
    
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
    
    if request.method == 'POST':
        post_data = request.POST
        with connection.cursor() as cursor:
            if 'reschedule' in post_data:
                appointment_id = post_data['reschedule']
                cursor.execute(f'''
                               SELECT work_day from accounts_availability AS ava
                               JOIN index_appointment AS app ON doctor_schedule_id = ava.id
                               WHERE app.id = {appointment_id}
                               ''')
                date = next_weekday_date(cursor.fetchall()[0][0])
                cursor.execute(f'''
                               INSERT INTO index_appointment (doctor_schedule_id, patient_id, date, status)
                               SELECT doctor_schedule_id, patient_id, "{date}", "p"
                               FROM index_appointment
                               WHERE id = {appointment_id}   
                               ''')
            else:
                appointment_id = post_data['cancel']

            cursor.execute(f'DELETE FROM index_appointment WHERE id={appointment_id}')
            
    __update_appointments(patient_id)
    context['appointment_list'] = __fetch_patient_appointment_list(patient_id)
    
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
                return render(request, 'index.html')
                
   
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
                    WHERE patient_id = {patient_id}
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
                (SELECT ava.id AS schedule_id, work_day, start_time, end_time
                FROM accounts_availability AS ava
                WHERE doctor_id={doctor['id']})
                EXCEPT
                (SELECT ava.id AS schedule_id, work_day, start_time, end_time 
                FROM accounts_availability as ava JOIN index_appointment ON doctor_schedule_id=ava.id
                WHERE patient_id={patient_id} AND status='p')
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
