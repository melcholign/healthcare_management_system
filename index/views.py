from django.shortcuts import render
from datetime import datetime, date
from django.db import connection
from util import dictfetchall, next_weekday_date, get_account_id

# Create your views here.
def home(request):
    return render(request, 'index.html')

def appointment_list(request):
    """ 
    Generates a list of appointments made by a patient
    """
    context = {}
    
    # Assuming that a logged-in patient account invoked this view
    account_data = request.session['account_data']
    patient_id = get_account_id(account_data['account_id'], account_data['account_type'])
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM index_appointment WHERE id={request.POST["cancel"]}')
            
    context['appointment_list'] = __fetch_appointment_list(patient_id)
    
    return render(request, 'appointment_list.html', context)

def make_appointment(request):
    """
    Provides the mechanisms by which valid appointments can be made
    """
    context = {}
    
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

def __fetch_appointment_list(patient_id):
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
