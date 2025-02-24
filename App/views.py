from django.shortcuts import render,redirect
from django.contrib.sessions.models import Session
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.decorators import login_required,login_not_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection
from django.db import DatabaseError
from django.urls import path

def create_tables():
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARBINARY(32) NOT NULL,
                address TEXT NOT NULL,
                district VARCHAR(100) NOT NULL,
                user_type ENUM('donor', 'trust') NOT NULL,
                is_approved BOOLEAN DEFAULT FALSE,
                mobile varchar(10) not null
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                image_path VARCHAR(200) NOT NULL,
                trust_id INT NOT NULL,
                district VARCHAR(100) NOT NULL,
                status
                FOREIGN KEY (trust_id) REFERENCES users(id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                image_path VARCHAR(200) DEFAULT NULL,
                donor_id INT NOT NULL,
                is_donated BOOLEAN DEFAULT FALSE,
                status BOOLEAN not null,
                FOREIGN KEY (donor_id) REFERENCES users(id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_id INT NOT NULL,
                trust_id INT NOT NULL,
                donor_id INT NOT NULL,
                progress ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                FOREIGN KEY (trust_id) REFERENCES users(id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact(
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,         
                mobile VARCHAR(10) NOT NULL,        
                email VARCHAR(255) NOT NULL,        
                subject VARCHAR(255) NOT NULL,      
                description TEXT,                   
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
            ); 
        """)

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

def home(request):
    return render(request, "index.html")

def about(request):
    return render(request,"about.html")

def contact(request):
    if request.method=="POST":
        name = request.POST['name']
        email=request.POST['email']
        mobile=request.POST['mobile']
        subject=request.POST['subject']
        description = request.POST['message']
        errors={}
        if len(name)<3 or len(name)>100:
                errors["Username"]="Username must be between 3 and 100 characters."

        try:
            validate_email(email)
        except ValidationError:
            errors["Email"]="Invalid email format."    
                
        if len(mobile)<10:
            errors["Phone Number"]="Mobile Number must contain 10 digits."

        if not subject:
            errors["Subject"]="Subject is Required."

        if not description:
            errors["Message"]="Message is Required."

        if errors:
            return render(request,"contact.html",{"errors":errors})

        query="INSERT INTO contact (name,mobile,email,subject,description) VALUES (%s,%s,%s,%s,%s)"
        params=[name,mobile,email,subject,description]
        execute_query(query,params)
    return render(request,"contact.html")

def privacy(request):
    return render(request,"privacy.html")

def error_page(request):
    return render(request, 'error.html', {'message': 'Something went wrong. Please try again later.'})
 

