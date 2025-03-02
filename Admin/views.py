from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.decorators import login_required,login_not_required
from django.core.validators import validate_email
import hashlib
from django.core.exceptions import ValidationError
from django.db import connection
from django.db import DatabaseError
from django.urls import reverse

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

def admin_panel(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'admin':
        return redirect('login')
    
    query="SELECT id, username, email,mobile, address, district FROM users WHERE user_type = 'trust' AND is_approved = FALSE"    
    pending_users = execute_query(query,fetch_one=False)
    return render(request, 'admin_panel.html', {'pending_users': pending_users})

def approve_user(request, user_id,username,email):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    query=" UPDATE users SET is_approved = TRUE WHERE is_approved=FALSE and id = %s"
    params=[user_id]
    execute_query(query,params,commit=True)
    send_mail(
        subject="🎉 Welcome to AidCare , Your Registration is Approved!",
        message="Dear {},\n\nWe are pleased to inform you that your registration with AidCare has been successfully verified and approved...\n\nBest Regards,\nAidCare Team".format(username),
        from_email="jeevajeevaloganathan977@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )
    messages.success(request,"User Approved Successfully and Email Notifiocation send to the Orphange User!")
    return render(request,'admin_panel.html')

def reject_user(request, user_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    query = "DELETE FROM users WHERE id = %s"
    params = [user_id]
    execute_query(query, params, commit=True)
    messages.success(request,"User Rejected Successfully!")
    return redirect('admin_panel')

def view_user(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    if request.method=="GET":
        query="SELECT id,username,email,district,user_type,mobile FROM users where user_type!='admin'"
        users=execute_query(query,fetch_one=False)
        return render(request,"view_user.html",{"users":users})
    return render(request,"view_user.html")

def insert_user(request):
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
            is_approved =True 
        elif user_type=='admin':
            is_approved =True
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

        if errors:
            return render(request,"insert_user.html",{"errors":errors})
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query="INSERT INTO users (username, email, password, address, district, user_type, is_approved,mobile) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
        params=[username, email, hashed_password, address, district, user_type, is_approved,mobile]
        execute_query(query,params,commit=True)
        messages.success(request,"User Account Inserted Successfully!")
        return redirect('view_user')
    
    return render(request, 'insert_user.html')

def update_user(request,user_id):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        mobile=request.POST['mobile']
        password = request.POST['password']
        cpassword=request.POST['cpassword']
        address = request.POST['address']
        district = request.POST['district']
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

        if errors:
            return render(request,"insert_user.html",{"errors":errors})
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query1="UPDATE users SET username=%s, email=%s, password=%s, address=%s, district=%s, user_type=%s, is_approved=%s,mobile=%s WHERE id=%s"
        params1=[username, email, hashed_password, address, district, user_type, is_approved,mobile,user_id]
        execute_query(query1,params1,commit=True)
        messages.success(request,"User Account Updated Successfully!")
        return redirect('view_user')
    
    return render(request, 'update_user.html')

def delete_user(request,user_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    if request.method=="POST":
        query="DELETE FROM users WHERE id=%s"
        params=[user_id]
        execute_query(query,params,commit=True)
        messages.success(request,"User Account Deleted Successfully!")
        return redirect('view_user') 
    return render(request,"view_user.html")

def contact_query(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    if request.method=="GET":
        query="SELECT * FROM contact"
        Queries=execute_query(query)
        return render(request,"view_contact.html",{"query":Queries})
    
    return render(request,"view_contact.html")

def delete_contact(request,contact_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    if request.method=="POST":
        query="Delete from contact where id=%s"
        params=[contact_id]
        execute_query(query,params,commit=True)
        messages.success(request,"Deleted User Query")
    return redirect('contact_query')

