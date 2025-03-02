from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.contrib import messages
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

def trust_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session.get('user_id')
    if not trust_id:
        return redirect('login')

    query="SELECT id, title, description, image_path FROM posts WHERE trust_id = %s"
    params=[trust_id]
    posts =execute_query(query,params,fetch_one=False)

    return render(request, 'trust_dashboard.html', {'posts': posts})

def view_request(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session.get('user_id')
    query="SELECT donors.username, donors.mobile, posts.title, requests.item_id, donors.email FROM users AS donors INNER JOIN requests ON requests.donor_id = donors.id INNER JOIN posts ON requests.item_id = posts.id WHERE requests.progress = 'pending' AND requests.trust_id = %s"
    params=[trust_id]
    requests=execute_query(query,params)
    return render(request,'view_request.html',{'requests':requests})
    
def view_donatedItems(request):
    if request.method=="GET": 
        query2=" SELECT p.id, p.title, p.description, p.image_path FROM posts p INNER JOIN requests r ON p.id = r.item_id WHERE r.progress = 'approved' AND p.status = 'donated'"
        historys = execute_query(query2, fetch_one=False)
        return render(request,'view_donated.html',{'historys':historys})
    return render(request,"view_donated.html")

def approve_request(request, request_id, email, username):
    if 'user_id' not in request.session or request.session.get('user_type') != 'trust':
        return redirect('login')
    trust_id = request.session.get("user_id")

    if request.method == "POST":
        query = "SELECT id FROM requests WHERE trust_id = %s AND item_id = %s"
        params = [trust_id, request_id]
        result = execute_query(query, params, fetch=True)

        if not result:
            messages.error(request, "Invalid request ID or unauthorized access.")
            return redirect('view_request')

        send_mail(
            subject="Your Donation Request Accepted",
            message=f"Dear {username},\n\nThank you! The orphanage has accepted your donation request. Our representative will contact you shortly.",
            from_email="jeevajeevaloganathan977@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )
        query = "UPDATE requests SET progress = 'approved' WHERE trust_id = %s AND item_id = %s"
        params = [trust_id, request_id]
        execute_query(query, params, commit=True)

        messages.success(request, "Approved Request and Email notification sent to the donor!")
        return redirect('view_request')

    return render(request, 'view_request.html')

def reject_request(request, request_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'trust':
        return redirect('login')
    trust_id=request.session.get("user_id")
    if request.method=="POST":
        query="UPDATE requests SET progress = 'rejected' WHERE trust_id=%s AND item_id = %s"
        params=[trust_id,request_id]
        execute_query(query, params, commit=True)
        messages.success(request,"Rejected Request!")
        return redirect('view_request')
    return render(request,"view_request.html")

def create_post(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session.get('user_id')
    if not trust_id:
        return redirect('login')
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        district = request.POST['district']
        image = request.FILES.get('image')
        valid_types = ["image/jpeg", "image/png", "image/jpg"] #accepted image format
        max_size = 2 * 1024 * 1024  # 2MB
        errors={}

        if len(title)<3 or len(title)>25:
            errors["Title"]="Post Title must be between 3 and 25 characters."
        if not description:
            errors["Description"]="Item Description is required."
        if not district:
            errors["District"]="Please select a district."
        if not image:
            errors["Image"]="Item Image is required."

        if image.content_type not in valid_types:
            errors["Image"]="Only JPG, PNG, and JPEG files are allowed."

        if image.size > max_size:
            errors['Image']="Image size must be less than 2MB."

        if errors:
            return render(request,"create_post.html",{"errors":errors})

        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_path = fs.url(filename)
            
        query="INSERT INTO posts (title, description, image_path, trust_id, district) VALUES (%s, %s, %s, %s, %s)"
        params=[title, description, image_path, trust_id, district]
        execute_query(query,params,commit=True)
        messages.success(request,"Post Created Successfully!")
        return redirect('trust_dashboard')   

    return render(request, 'create_post.html')

def delete_post(request, post_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session.get('user_id')
    if not trust_id:
        return redirect('login')

    query="SELECT id FROM posts WHERE id = %s AND trust_id = %s"
    params=[post_id, trust_id]
    post =execute_query(query,params,fetch_one=True)
    if post:
        query1="DELETE FROM posts WHERE id = %s"
        params=[post_id]
        execute_query(query1,params,commit=True)
        messages.success(request,"Post Deleted Successfully!")
    return redirect('trust_dashboard')