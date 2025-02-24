from django.shortcuts import render,redirect
from django.contrib.sessions.models import Session
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.decorators import login_required,login_not_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection
import hashlib
from django.db import DatabaseError
from django.urls import path

def execute_query(query,params=None,fetch_one=False,commit=False):
    #try:
        with connection.cursor() as cursor:
            cursor.execute(query,params or [])
            if commit:
                connection.commit()
                return cursor.rowcount
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    #except Exception as e:
    #    redirect('error')
    
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        mobile=request.POST['mobile']
        password = request.POST['password']
        cpassword=request.POST['cpassword']
        address = request.POST['address']
        district = request.POST['district']
        agree=request.POST.get('agree')
        user_type = request.POST['user_type']
        if user_type == 'donor':
            is_approved = True 
        else:
            is_approved =False

        errors={}

        if len(username)<3 or len(username)>100:
            errors["Username"]="Username must be between 3 and 100 characters."

        try:
            validate_email(email)
        except ValidationError:
            errors["Email"]="Invalid email format."    
            
        if len(mobile)<10:
            errors["Phone Number"]="Mobile Number must contain 10 digits."

        if (len(password)<8 or not any(char.isupper() for char in password) \
            or not any(char.islower() for char in password) or not any(char.isdigit() for char in password) \
            or not any(char in "!@#$%^&*" for char in password)):
            errors["Password"]="Password must be atleast 8 characters long and include uppercase, lowercase, a number, and a special character."

        if cpassword!=password:
            errors["Confirm Password"]="Password do not match."

        if not address.strip():
            errors["Address"]="Address is required."

        if not district:
            errors["District"]="Please select a district."

        if user_type not in["donor","trust"]:
            errors["User Type"]="Invalid user type."

        if not agree:
            errors['checkbox']="You must agree to the terms and conditions."

        if errors:
            return render(request,"register.html",{"errors":errors})
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query="INSERT INTO users (username, email, password, address, district, user_type, is_approved,mobile) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
        params=[username, email, hashed_password, address, district, user_type, is_approved,mobile]
        execute_query(query,params,commit=True)

        if not is_approved:
            return render(request, 'pending_approval.html')
        return redirect('login')
    
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        query = "SELECT id, user_type, is_approved, password FROM users WHERE username = %s"
        params = [username]
        user = execute_query(query, params, fetch_one=True)

        if not user[2]:  
            return render(request, 'login.html', {'error': 'Account pending approval'})
        
        if user:
            stored_hashed_password = user[3]  
            entered_hashed_password = hashlib.sha256(password.encode()).hexdigest() 

            if stored_hashed_password == entered_hashed_password:
                request.session['user_id'] = user[0]
                request.session['user_type'] = user[1]
                if user[1] == 'donor':
                    return redirect('donor_dashboard')
                elif user[1] == 'trust':
                    return redirect('trust_dashboard')
                elif user[1]=='admin':
                    return redirect('admin_panel')
            else:
                return render(request, 'login.html', {'error': 'Incorrect Password'})
        else:       
            return render(request, 'login.html', {'error': 'User not found'})
    return render(request, 'login.html')

def logout(request):
    request.session.flush()
    return redirect('home')