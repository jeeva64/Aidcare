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
                password VARCHAR(100) NOT NULL,
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
                progress ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                FOREIGN KEY (trust_id) REFERENCES users(id)
            );
        """)

def execute_query(query,params=None,fetch_one=False,commit=False):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query,params)
            if commit:
                connection.commit()
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {e}")
        return None        

def home(request):
    return render(request, "index.html")

def about(request):
    return render(request,"about.html")

def register(request):
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
            errors["username"]="Username must be between 3 and 100 characters."

        try:
            validate_email(email)
        except ValidationError:
            errors["email"]="Invalid email format."    
            
        if len(mobile)<10:
            errors["Phone Number"]="Mobile Number must contain 10 digits."

        if (len(password)<8 or not any(char.isupper() for char in password) \
            or not any(char.islower() for char in password) or not any(char.isdigit() for char in password) \
            or not any(char in "!@#$%^&*" for char in password)):
            errors["password"]="Password must be atleast 8 characters long and include uppercase, lowercase, a number, and a special character."

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
        
        query="INSERT INTO users (username, email, password, address, district, user_type, is_approved,mobile) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
        params=[username, email, password, address, district, user_type, is_approved,mobile]
        execute_query(query,params,commit=True)

        if not is_approved:
            return render(request, 'pending_approval.html')
        return redirect('login')
    
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        query="SELECT id, user_type, is_approved FROM users WHERE username = %s AND password = %s"
        params=[username, password]
        user=execute_query(query,params,fetch_one=True)

        if user:
            if not user[2]:  
                return render(request, 'login.html', {'error': 'Account pending approval'})
            request.session['user_id'] = user[0]
            request.session['user_type'] = user[1]
            if user[1] == 'donor':
                return redirect('donor_dashboard')
            elif user[1] == 'trust':
                return redirect('trust_dashboard')
            elif user[1]=='admin':
                return redirect('admin_panel')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def donor_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'donor':
        return redirect('login')
    donor_id = request.session.get('user_id')
    if not donor_id:
        return redirect('login')

    query="SELECT district FROM users WHERE id = %s"
    params=[donor_id]
    donor_district = execute_query(query,params,fetch_one=True)[0]

    query1="SELECT posts.id, posts.title, posts.description, posts.image_path,posts.trust_id, users.username FROM posts INNER JOIN users ON posts.trust_id = users.id WHERE posts.district = %s AND users.is_approved = TRUE"
    params1=[donor_district]
    posts = execute_query(query1,params1,fetch_one=False)
    return render(request, 'donor_dashboard.html', {'posts': posts})

def donate(request,post_id,trust_id):
    if request.method == 'POST' and 'user_id' in request.session:
        donor_id = request.session.get('user_id')
        if not donor_id:
            return redirect('login')

        query="update posts set status=TRUE where id=%s and trust_id=%s"
        params=[post_id,trust_id]
        execute_query(query,params,commit=True)

        query1=" INSERT INTO requests (item_id,trust_id,donor_id,progress)VALUES (%s, %s,%s,%s)"
        params1=[post_id,trust_id,donor_id,"pending"]
        execute_query(query1,params1,commit=True)

    return redirect('donor_dashboard')

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

        query="INSERT INTO inventory (name, description, image_path, donor_id, is_donated) VALUES (%s, %s, %s, %s, %s)"
        params=[name, description, image_path, donor_id, False]
        execute_query(query,params,commit=True)
        return redirect('inventory')

    return render(request, 'add_item.html')

def inventory(request):
    if 'user_id' in request.session and request.method=="GET":
        donor_id=request.session['user_id']
        if not donor_id:
            return redirect('login')

        query="SELECT id,name,description,image_path from inventory where donor_id=%s and is_donated=FALSE"
        params=[donor_id]
        inventorys=execute_query(query,params,fetch_one=False)

        query1="SELECT id,name,description,image_path from inventory where donor_id=%s and is_donated=TRUE"
        params1= [donor_id]
        historys=execute_query(query1,params1,fetch_one=False)
        return render(request,'inventory.html',{'inventorys':inventorys,'historys':historys})
    return render(request,'inventory.html')     

def mark_as_donated(request, item_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'donor':
        return redirect('login')
    if request.method=="GET":
        donor_id = request.session.get('user_id')
        if not donor_id:
            return redirect('login')

        query=" UPDATE inventory SET is_donated = TRUE WHERE id = %s AND donor_id = %s"
        params= [item_id, donor_id]
        execute_query(query,params,commit=True)
        return redirect('inventory')
    return render(request,'inventory.html')

def delete_inventory(request,id):
    if 'user_id' in request.session and request.method=="GET":
        donor_id=request.session['user_id']
        if not donor_id:
            return redirect('login')

        query="DELETE from inventory where id=%s and donor_id=%s"
        params=[id,donor_id]
        execute_query(query,params,commit=True)
        return redirect('inventory')   
    return render(request,'inventory.html') 

def trust_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session['user_id']
    if not trust_id:
        return redirect('login')

    query="SELECT id, title, description, image_path FROM posts WHERE trust_id = %s"
    params=[trust_id]
    posts =execute_query(query,params,fetch_one=False)

    return render(request, 'trust_dashboard.html', {'posts': posts})

def view_request(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session['user_id']
    if not trust_id:
        return redirect('login')

    query="SELECT users.username,users.mobile,posts.title,requests.id FROM users INNER JOIN posts ON users.id = posts.trust_id INNER JOIN requests ON requests.post_id = posts.id WHERE requests.progress = %s AND requests.trust_id = %s"
    params=["pending", trust_id]
    requests=execute_query(query,params,fetch_one=False)

    return render(request,'view_request.html',{'requests':requests})

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
            
        query="INSERT INTO posts (title, description, image_path, trust_id, district) VALUES (%s, %s, %s, %s, %s)"
        params=[title, description, image_path, trust_id, district]
        execute_query(query,params,commit=True)
    
        return redirect('trust_dashboard')   

    return render(request, 'create_post.html')

def delete_post(request, post_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'trust':
        return redirect('login')
    trust_id = request.session['user_id']
    if not trust_id:
        return redirect('login')

    query="SELECT id FROM posts WHERE id = %s AND trust_id = %s"
    params=[post_id, trust_id]
    post =execute_query(query,params,fetch_one=True)
    if post:
        query1="DELETE FROM posts WHERE id = %s"
        params=[post_id]
        execute_query(query1,params,commit=True)
    return redirect('trust_dashboard')

def admin_panel(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'admin':
        return redirect('login')
    admin_id = request.session['user_id']
    if not admin_id:
        return redirect('login')
    
    query="SELECT id, username, email,mobile, address, district FROM users WHERE user_type = 'trust' AND is_approved = FALSE"    
    pending_users = execute_query(query,fetch_one=False)
    return render(request, 'admin_panel.html', {'pending_users': pending_users})

def approve_user(request, user_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'admin':
        return redirect('login')
    
    if request.method=="POST":
        query=" UPDATE users SET is_approved = TRUE WHERE is_approved=FALSE and id = %s"
        params=[user_id]
        execute_query(query,params,commit=True)
        return redirect('admin_panel')
    return render(request,'admin_panel.html')

def logout(request):
    request.session.flush()
    return redirect('home')
