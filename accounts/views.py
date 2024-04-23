from django.shortcuts import render
from django.db import connection
from django.contrib.auth.models import User
from datetime import date


def registerDoctor(request):
    cursor = connection.cursor()
    cursor.execute('SELECT name, address from accounts_institution')
    institutions = cursor.fetchall()
    
    context = {
        'workplaces': institutions,
    }
    
    if request.method == "POST":
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
                    
    return render(request, 'registerDoctor.html', context=context)

def registerPatient(request):
    cursor = connection.cursor()
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        date_of_birth = request.POST['date_of_birth']
        sex = request.POST['sex']
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

    return render(request, 'registerPatient.html')


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        cursor = connection.cursor()

        # Check if the user exists
        userQuery = "SELECT * FROM auth_user WHERE email = %s AND password = %s"
        cursor.execute(userQuery, [email, password])
        results = cursor.fetchall()
        if len(results) > 0:
            user = results[0]
            request.session['user_id'] = user[0]
            request.session['email'] = user[1]
            return render(request, 'index.html')
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password'})
        
    return render(request, 'login.html')