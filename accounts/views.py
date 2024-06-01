from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from datetime import date
from util.functions import *
from util.decorators import account_permission
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@account_permission('doctor')
def schedules(request):
    """
    Create, update, and delete schedules of a doctor
    """
    doctor_id = get_account_id(request.session['account_data']['account_id'], request.session['account_data']['account_type'])
    
    if request.method == 'GET':
        with connection.cursor() as cursor:
            
            # Get all the doctor's schedules that have not been set as deleted
            cursor.execute(f'''
                           SELECT id, work_day, start_time, end_time
                           FROM accounts_availability
                           WHERE doctor_id = {doctor_id} AND deleted = 0
                           ''')
            schedules = dictfetchall(cursor)
            for schedule in schedules:
                schedule['work_day_full'] = get_full_weekday_name(schedule['work_day'])
                schedule['start_time'] = str(schedule['start_time'])
                schedule['end_time'] = str(schedule['end_time'])
                        
        return render(request, 'schedules.html', {'schedules': schedules})
    
    if request.method == 'POST':

        print(json.loads(request.body))

        created = json.loads(request.body)
             
        with connection.cursor() as cursor:
            cursor.execute(f'''
                           INSERT INTO accounts_availability (doctor_id, work_day, start_time, end_time, deleted)
                           VALUES ({doctor_id}, '{created['work_day']}', '{created['start_time']}', '{created['end_time']}', 0)
                           ''')
            
            new_schedule_id = cursor.lastrowid
        
        return JsonResponse(new_schedule_id, safe=False)
                    
    if request.method == 'DELETE':
        deleted = json.loads(request.body)
        
        with connection.cursor() as cursor:
            
            # check the schedule is a dependency of some appointment records
            cursor.execute(f'''
                           SELECT * FROM index_appointment
                           WHERE doctor_schedule_id = {deleted['id']}
                           ''')
            
            dependants = dictfetchall(cursor)
                        
            # if some records depend on the selected schedule, then set its deleted attribute to 1
            # else delete the schedule from the database
            if dependants:
                cursor.execute(f'''
                               UPDATE accounts_availability
                               SET deleted = 1
                               WHERE id = {deleted['id']}
                               ''')
                
            else:
                cursor.execute(f'''
                            DELETE FROM accounts_availability
                            WHERE id = {deleted['id']}
                            ''')
            
        return HttpResponse(status=200)
    

@account_permission('doctor')
def change_availability(request):
    
    """
    Updates if a doctor is available or not
    """
    
    with connection.cursor() as cursor:
        cursor.execute(f'''
                        UPDATE accounts_doctor
                        SET available = 
                            CASE
                                WHEN available = 0 THEN 1
                                ELSE 0
                            END
                        WHERE user_id = {request.session['account_data']['account_id']}
                        ''')
    
    return HttpResponseRedirect(reverse('account_page'))

# def isLoggedIn(request):
#     session_data = request.session
#     if 'account_data' in session_data:    
#         return True
#     else:
#         return False
    
def configureNavBar(request, context):
    
    if 'account_data' in request.session:
        account_data = request.session['account_data']
        
        with connection.cursor() as cursor:
            cursor.execute(f'''select first_name, last_name from auth_user where id = {account_data['account_id']}''')
            row = cursor.fetchone()
            
            context['firstName'] = row[0]
            context['lastName'] = row[1] 
            context['account_type'] = account_data['account_type']
            context["isLoggedIn"] = True


def registerDoctor(request):
    cursor = connection.cursor()
    cursor.execute('SELECT name, address from accounts_institution')
    institutions = cursor.fetchall()
    
    context = {
        'workplaces': institutions,
    }
    configureNavBar(request, context)
    
    if request.method == "POST":
        print("form accessed")
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        specialty = request.POST['specialty']
        department = request.POST['department']
        qualification = request.POST['qualification']
        workplace = request.POST['workplace']
        email = request.POST['email']
        contact = request.POST['contact']
        password = request.POST['password']
        
        cursor.execute(f'SELECT email from auth_user where email = \'{email}\'')
        if cursor.fetchall():
            context['error_message'] = 'Doctor with this email already exists'
        else:    
            # Create a new user instance for the doctor
            username = email[0:email.find('@')]
            userInsertQuery = '''INSERT INTO auth_user(username, email, password, first_name, last_name, date_joined, is_superuser, is_staff, is_active)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(userInsertQuery, [username, email, password,  first_name, last_name, date.today(), False, False, True])

            # Get the ID of the inserted user
            user_id = cursor.lastrowid

            doctorInsertQuery = """
                INSERT INTO accounts_doctor(user_id, specialty, department, qualification, workplace_id, contact, available) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(doctorInsertQuery, [user_id, specialty, department, qualification, workplace, contact, False])
            return redirect("/")
                    
    return render(request, 'registerDoctor.html', context=context)

def registerPatient(request):
    context = {}
    configureNavBar(request, context)
    cursor = connection.cursor()
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        date_of_birth = request.POST['date_of_birth']
        sex = request.POST['gender']
        address = request.POST['address']
        contact = request.POST['contact']
        email = request.POST['email']
        password = request.POST['password']

        # Check if patient with the same email already exists
        patientQuery = "SELECT * FROM auth_user WHERE email = %s"
        cursor.execute(patientQuery, [email])
        results = cursor.fetchall()
        if len(results) > 0:
            return render(request, 'registerPatient.html', {'error': 'Patient with this email already exists'})
        else:
            # Create a new user instance for the patient
            username = email[0:email.find('@')]
            userInsertQuery = '''INSERT INTO auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
             values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(userInsertQuery, [password, False, username, first_name, last_name, email, False, True, date.today()])
            user_id = cursor.lastrowid

            # Insert data into accounts_patient table
            patientInsertQuery = """
                INSERT INTO accounts_patient(user_id, date_of_birth, sex, address, contact) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(patientInsertQuery, [user_id, date_of_birth, sex, address, contact])
            return redirect("/")

    return render(request, 'registerPatient.html')


def account_login(request):
    session_data = request.session
    
    print(session_data)
        
    if 'account_data' in session_data:    
        return redirect("/")
    
    context = {}
    configureNavBar(request, context)
    
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        
        with connection.cursor() as cursor:
            # Check if the user exists
            userQuery = "SELECT * FROM auth_user WHERE email = %s AND password = %s"
            cursor.execute(userQuery, [email, password])
            results = dictfetchall(cursor)
            
        if results:
            user = results[0]
            session_data['account_data'] = {
                'account_id': user['id'],
                'account_type': __get_account_type(user['id']),
            }
            
            print(request.session['account_data'])
            
            return redirect("/")

        else:
            context['error_message'] = 'Invalid email or password'
            
    return render(request, 'account_login.html', context)

def account_logout(request):
    try:
        del request.session['account_data']
    except KeyError:
        pass
    
    return HttpResponseRedirect(reverse('account_login'))

def get_account_page(request):
    if 'account_data' not in request.session:
        HttpResponseRedirect(reverse('account_login'))
        
    template_name = 'doctor_dashboard.html' if request.session['account_data']['account_type'] == 'doctor' else 'patient_portal.html'
    return render(request, template_name)

def __get_account_type(user_id):
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * from accounts_doctor where user_id={user_id}')
        return 'doctor' if cursor.fetchall() else 'patient'