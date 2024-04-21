from django.shortcuts import render
from django.db import connection
from django.contrib.auth.models import User
from datetime import date


def registerDoctor(request):
    cursor = connection.cursor()
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        specialty = request.POST['specialty']
        department = request.POST['department']
        qualification = request.POST['qualification']
        email = request.POST['email']
        contact = request.POST['contact']
        password = request.POST['password']
        
        username = email[0:email.find('@')]
        
        # Create a new user instance for the doctor
        userInsertQuery = '''INSERT INTO auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
             values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(userInsertQuery, [password, False, username, first_name, last_name, email, False, True, date.today()])

        # Get the ID of the inserted user
        doctor = cursor.lastrowid

        doctorInsertQuery = """
            INSERT INTO accounts_doctor(id, specialty, department, qualification, contact) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(doctorInsertQuery, [user_id, specialty, department, qualification, contact])
    return render(request, 'registerDoctor.html')



def registerPatient(request):
    cursor = connection.cursor()
    if request.method == "POST":
        name = request.POST['name']
        dateOfBirth = request.POST['dateOfBirth']
        gender = request.POST['gender']
        address = request.POST['address']
        phoneNumber = request.POST['phoneNumber']
        email = request.POST['email']
        password = request.POST['password']

        # Check if patient with the same email already exists
        patientQuery = "SELECT * FROM accounts_patient WHERE email = %s"
        cursor.execute(patientQuery, [email])
        results = cursor.fetchall()
        if len(results) > 0:
            return render(request, 'registerPatient.html', {'error': 'Patient with this email already exists'})
        else:
            # Create a new user instance for the patient
            userInsertQuery = "INSERT INTO auth_user(username, password) VALUES (%s, %s)"
            cursor.execute(userInsertQuery, [email, password])
            user_id = cursor.lastrowid

            # Insert data into accounts_patient table
            patientInsertQuery = """
                INSERT INTO accounts_patient(user_id, name, dateOfBirth, gender, address, contact, email) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(patientInsertQuery, [user_id, name, dateOfBirth, gender, address, phoneNumber, email])

    return render(request, 'registerPatient.html')


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        cursor = connection.cursor()

        # Check if the user exists
        userQuery = "SELECT * FROM auth_user WHERE username = %s AND password = %s"
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