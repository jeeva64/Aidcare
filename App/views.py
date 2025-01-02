from django.shortcuts import render,redirect
from django.contrib.sessions.models import Session
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.decorators import login_required,login_not_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection
from django.urls import path

def create_tables():
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                address TEXT NOT NULL,
                district VARCHAR(100) NOT NULL,
                user_type ENUM('donor', 'trust') NOT NULL,
                is_approved BOOLEAN DEFAULT FALSE
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
                FOREIGN KEY (donor_id) REFERENCES users(id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_id INT NOT NULL,
                trust_id INT NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                FOREIGN KEY (item_id) REFERENCES inventory(id),
                FOREIGN KEY (trust_id) REFERENCES users(id)
            );
        """)

def home(request):
    return render(request, "index.html")

def about(request):
    return render(request,"about.html")

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
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

        if len(username)<3:
            errors["username"]="Username must be at least 3 characters long."

        try:
            validate_email(email)
        except ValidationError:
            errors["email"]="Invalid email format."    
            
        if len(password)<8:
            errors["password"]="Password must be atleast 8 characters long."

        if cpassword!=password:
            errors["confirmpassword"]="Password do not match."

        if not address.strip():
            errors["address"]="Address is required."

        if not district:
            errors["district"]="Please select a district."

        if user_type not in["donor","trust"]:
            errors["user_type"]="Invalid user type."

        if errors:
            return render(request,"register.html",{"errors":errors})
                            
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, email, password, address, district, user_type, is_approved)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [username, email, password, address, district, user_type, is_approved])

        if not is_approved:
            return render(request, 'pending_approval.html')
        return redirect('login')
    
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_type, is_approved FROM users 
                WHERE username = %s AND password = %s""", [username, password])
            user = cursor.fetchone()

        if user:
            if not user[2]:  
                return render(request, 'login.html', {'error': 'Account pending approval'})
            request.session['user_id'] = user[0]
            request.session['user_type'] = user[1]
            if user[1] == 'donor':
                return redirect('donor_dashboard')
            elif user[1] == 'trust':
                return redirect('trust_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def trust_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session['user_id']
    if not trust_id:
        return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, description, image_path FROM posts WHERE trust_id = %s
        """, [trust_id])
        posts = cursor.fetchall()

    return render(request, 'trust_dashboard.html', {'posts': posts})

def donor_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'donor':
        return redirect('login')
    donor_id = request.session.get('user_id')
    if not donor_id:
        return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("SELECT district FROM users WHERE id = %s", [donor_id])
        donor_district = cursor.fetchone()[0]

        cursor.execute("""
            SELECT posts.id, posts.title, posts.description, posts.image_path, users.username
            FROM posts
            INNER JOIN users ON posts.trust_id = users.id
            WHERE posts.district = %s AND users.is_approved = TRUE
        """, [donor_district])
        posts = cursor.fetchall()
    return render(request, 'donor_dashboard.html', {'posts': posts})

def add_item(request):
    if request.method == 'POST' and 'user_id' in request.session and request.FILES['product']:
        donor_id = request.session.get('user_id')
        if not donor_id:
            return redirect('login')
        name = request.POST['name']
        description = request.POST['description']
        image = request.FILES['product']
        image_path=None
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_path = fs.url(filename)
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO inventory (name, description, image_path, donor_id, is_donated)
                VALUES (%s, %s, %s, %s, %s)
            """, [name, description, image_path, donor_id, False])
        return redirect('donor_dashboard')
    return render(request, 'add_item.html')

def inventory(request):
    if 'user_id' in request.session:
        donor_id=request.session['user_id']
        if not donor_id:
            return redirect('login')
        with connection.cursor() as cursor:
            cursor.execute("""SELECT id,name,description,image_path from inventory where donor_id=%s""",[donor_id])
            inventorys=cursor.fetchall()
    return render(request,'inventory.html',{'inventorys':inventorys})     

def delete_inventory(request,id):
    if 'user_id' in request.session:
        donor_id=request.session['user_id']
        if not donor_id:
            return redirect('login')
        with connection.cursor() as cursor:
            cursor.execute("""DELETE from inventory where id=%s and donor_id=%s""",[id,donor_id])
        return redirect(donor_dashboard)   
    return render(request,'donor_dashboard.html') 

def create_post(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session['user_id']
    if not trust_id:
        return redirect('login')
    if request.method == 'POST' and request.FILES['image']:
        title = request.POST['title']
        description = request.POST['description']
        district = request.POST['district']
        image = request.FILES['image']

        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_path = fs.url(filename)
            
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO posts (title, description, image_path, trust_id, district)
                VALUES (%s, %s, %s, %s, %s)
                """, [title, description, image_path, trust_id, district])
        return redirect('trust_dashboard')   

    return render(request, 'create_post.html')

def delete_post(request, post_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')

    trust_id = request.session['user_id']
    if not trust_id:
        return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM posts WHERE id = %s AND trust_id = %s", [post_id, trust_id])
        post = cursor.fetchone()
        if post:
            cursor.execute("DELETE FROM posts WHERE id = %s", [post_id])

    return redirect('trust_dashboard')

def mark_as_donated(request, item_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'donor':
        return redirect('login')

    donor_id = request.session.get('user_id')
    if not donor_id:
        return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE inventory SET is_donated = TRUE WHERE id = %s AND donor_id = %s
        """, [item_id, donor_id])

    return redirect('donor_dashboard')

def admin_panel(request):
    if 'is_admin' not in request.session or not request.session['is_admin']:
        return redirect('login') 
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username, email, address, district 
            FROM users 
            WHERE user_type = 'trust' AND is_approved = FALSE
        """)
        pending_users = cursor.fetchall()

    return render(request, 'admin/admin_panel.html', {'pending_users': pending_users})


def approve_user(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE users SET is_approved = TRUE WHERE id = %s
        """, [user_id])

    return redirect('admin_panel')

def logout(request):
    request.session.flush()
    return redirect('home')
