from django.shortcuts import render,redirect
from django.contrib.sessions.models import Session
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.decorators import login_required,login_not_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection
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

def admin_panel(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'admin':
        return redirect('login')
    
    query="SELECT id, username, email,mobile, address, district FROM users WHERE user_type = 'trust' AND is_approved = FALSE"    
    pending_users = execute_query(query,fetch_one=False)
    return render(request, 'admin_panel.html', {'pending_users': pending_users})

def approve_user(request, user_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    query=" UPDATE users SET is_approved = TRUE WHERE is_approved=FALSE and id = %s"
    params=[user_id]
    execute_query(query,params,commit=True)
    return render(request,'admin_panel.html')

def reject_user(request, user_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    query = "DELETE FROM users WHERE id = %s"
    params = [user_id]
    execute_query(query, params, commit=True)
    return redirect('admin_panel')

def contact_query(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'admin':
        return redirect('login')
    if request.method=="GET":
        query="SELECT * FROM contact"
        Queries=execute_query(query)
        return render(request,"view_contact.html",{"query":Queries})
    
    return render(request,"view_contact.html")


