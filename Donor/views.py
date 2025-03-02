from django.shortcuts import render,redirect
from django.contrib import messages
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

def donor_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'donor':
        return redirect('login')
    donor_id = request.session.get('user_id')

    query="SELECT district FROM users WHERE id = %s"
    params=[donor_id]
    donor_district = execute_query(query,params,fetch_one=True)[0]

    query1="SELECT posts.id, posts.title, posts.description, posts.image_path,posts.trust_id, users.username FROM posts INNER JOIN users ON posts.trust_id = users.id WHERE users.is_approved = TRUE and posts.status=%s and posts.district = %s"
    params1=["pending",donor_district]
    posts = execute_query(query1,params1,fetch_one=False)
    return render(request, 'donor_dashboard.html', {'posts': posts})

def donate(request,post_id,trust_id):
    if request.method != 'POST' or 'user_id' not in request.session:
        return redirect('login')
    donor_id = request.session.get('user_id')

    query="UPDATE posts SET status = 'donated' WHERE id = %s AND trust_id = %s"
    params=[post_id, trust_id]
    execute_query(query,params,commit=True)
    
    query1="INSERT INTO requests (item_id, trust_id, donor_id, progress) VALUES (%s, %s, %s, %s)"
    params1=[post_id, trust_id, donor_id, "pending"]
    execute_query(query1,params1,commit=True)
    messages.success(request,"Donated Successfully!")
    return redirect('donor_dashboard')

def add_item(request):
    if request.method == 'POST' and 'user_id' in request.session:
        donor_id = request.session.get('user_id')
        
        name = request.POST['name']
        description = request.POST['description']
        image = request.FILES.get('product')
        valid_types = ["image/jpeg", "image/png", "image/jpg"] #accepted image format
        max_size = 2 * 1024 * 1024  # 2MB
        errors={}

        if len(name)<3 or len(name)>25:
            errors["Item Name"]="Itemname must be between 3 and 25 characters."
        if not description:
            errors["Description"]="Item Description is required."
        if not image:
            errors["Image"]="Item Image is required."
        
        if image.content_type not in valid_types:
            errors["Image"]="Only JPG, PNG, and JPEG files are allowed."

        if image.size > max_size:
            errors['Image']="Image size must be less than 2MB."

        if errors:
            return render(request,"add_item.html",{"errors":errors})

        image_path=None
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_path = fs.url(filename)

        query="INSERT INTO inventory (name, description, image_path, donor_id, is_donated) VALUES (%s, %s, %s, %s, %s)"
        params=[name, description, image_path, donor_id, False]
        execute_query(query,params,commit=True)
        messages.success(request,"Product Added Successfully")
        return redirect('inventory')

    return render(request, 'add_item.html')

def inventory(request):
    if 'user_id' in request.session and request.method=="GET":
        donor_id=request.session.get('user_id')
    if request.method=="GET":
        query="SELECT id,name,description,image_path from inventory where donor_id=%s and is_donated=FALSE"
        params=[donor_id]
        inventorys=execute_query(query,params,fetch_one=False)

        query2=" SELECT p.id, p.title, p.description, p.image_path FROM posts p INNER JOIN requests r ON p.id = r.item_id WHERE r.progress = 'approved' AND r.donor_id = %s AND p.status = 'donated'"
        historys = execute_query(query2, [donor_id], fetch_one=False)
        return render(request,'inventory.html',{'inventorys':inventorys,'historys':historys})
    return render(request,'inventory.html')     

def donation_history(request):
    if 'user_id' in request.session and request.method=="GET":
        donor_id=request.session.get('user_id')
    if request.method=="GET": 
        query2=" SELECT p.id, p.title, p.description, p.image_path FROM posts p INNER JOIN requests r ON p.id = r.item_id WHERE r.progress = 'approved' AND r.donor_id = %s AND p.status = 'donated'"
        historys = execute_query(query2, [donor_id], fetch_one=False)
        return render(request,'donation_history.html',{'historys':historys})
    return render(request,'donation_history.html') 

def delete_inventory(request,id):
    if 'user_id' in request.session and request.method=="GET":
        donor_id=request.session.get('user_id')
        if not donor_id:
            return redirect('login')

        query="DELETE from inventory where id=%s and donor_id=%s"
        params=[id,donor_id]
        execute_query(query,params,commit=True)
        messages.success(request,"Deleted Inventory Successfully!")
        return redirect('inventory')   
    return render(request,'inventory.html')