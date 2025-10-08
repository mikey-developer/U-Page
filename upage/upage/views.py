from django.shortcuts import render, redirect, HttpResponse
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from MySQLdb.cursors import DictCursor
from django.conf import settings
import time
import os
from datetime import datetime

now = datetime.now()
fdata = now.strftime("%d-%m-%y / %H:%M")


def home(request):
    return render(request, "index.html")

def center(request):
    return render(request, "center.html")

def post_details(request, id):
    if "id" not in request.session:
        return redirect("login")

    with connection.cursor() as sql:
        sql.execute("SELECT * FROM posts WHERE id = %s", [id])
        row = sql.fetchone()

    if row:
        post = {
            "id": row[0],
            "user_id": row[1],
        }
    else:
        post = None

    return render(request, "post-details.html", {
        "post": post,
        "session_id": str(request.session["id"])
    })


def publication_edit(request, id):
    with connection.cursor() as sql:
        sql.execute("SELECT * FROM posts WHERE id = %s", [id])
        values = sql.fetchone()
        if request.method == "POST":
            content = request.POST['content']
            mysql = """
                    UPDATE posts SET content = %s, ifedited = %s WHERE id = %s
                """
            with connection.cursor() as sql:
                sql.execute(mysql, [content, 1, id])
            return redirect("home")
    return render(request, "post-edit.html", {'values': values})

def publication(request):
    if request.method == "POST":
        content = request.POST['content']
        mysql = """
                    INSERT INTO posts 
                    (id, user_id, content, time_is)
                    VALUES 
                    (NULL, %s, %s, %s)
                """
        with connection.cursor() as sql:
            sql.execute(mysql, [request.session['id'], content, fdata])
            # sql.execute("INSERT INTO posts (id, user_id, content) VALUES (NULL, %s, %s)", [request.session['id'], content])

        return redirect("home")
    return render(request, "publication.html")

def publication_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        img = request.FILES["image"]
        content = request.POST['content']
        
        filename = f"{int(time.time())}_{img.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        with open(file_path, "wb+") as destination:
            for chunk in img.chunks():
                destination.write(chunk)

        file_url = f"{settings.MEDIA_URL}{filename}"

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO posts (id, user_id, content, time_is, photo) VALUES (NULL, %s, %s, %s, %s)", 
                [request.session['id'], content, fdata, file_url]
            )

        return redirect('home')
    return render(request, 'img-publication.html')
 

def publication_delete(request, id):
    with connection.cursor() as cursor:
        # Avval postni olish (rasm yo‘lini)
        cursor.execute("SELECT * FROM posts WHERE id = %s", [id])
        data = cursor.fetchone()

    if data:
        pic_url = data[5]  # rasm ustuni
        if pic_url:
            file_path = pic_url.replace("/media/", "")
            absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)

            if os.path.exists(absolute_path):
                os.remove(absolute_path)

        # Keyin postni o‘chirish
        with connection.cursor() as sql:
            sql.execute("DELETE FROM posts WHERE id = %s", [id])

    return redirect('home')

    # return render(request, "publication.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST['uname']
        raw_password = request.POST['passw']
        hashed_password = make_password(raw_password)

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", [username])
            existing_user = cursor.fetchone()

        if existing_user:
            return render(request, 'signup.html', {'error': 'Username already taken'})

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                [username, hashed_password]
            )

        return redirect('login')

    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        raw_password = request.POST['password'].strip()

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password FROM users WHERE username = %s", [username])
            user = cursor.fetchone()

        if user and check_password(raw_password, user[1]):
            request.session['id'] = user[0]
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def user_profile(request, id):
    with connection.cursor() as sql:
        sql.execute("SELECT * FROM users WHERE username = %s", [id])
        user = sql.fetchone()
    return render(request, "me.html", {
        "user" : user
    })


def home(request):
    if 'id' not in request.session:
        return redirect('login')

    posts_with_users = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts ORDER BY id DESC")
        posts = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", [request.session['id']])
        userpic = cursor.fetchone()
        # pic = userpic[1]

    with connection.cursor() as cursor:
        for p in posts:
            cursor.execute("SELECT * FROM users WHERE id = %s", [p[1]])  # p[1] = user_id
            user = cursor.fetchone()   # faqat bitta user
            posts_with_users.append({
                'post': p,
                'user': user, 
            })

    return render(request, 'index.html', {'posts': posts_with_users,   'pic': userpic})


def user(request, id):
    with connection.cursor() as sql:
        sql.execute(f"SELECT * FROM users WHERE id = {id}")
        rows = sql.fetchone()
    return render(request, "users.html", {'users':rows})

def posts(request, id):
    if 'id' not in request.session:
        return redirect('login')

    posts_with_users = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts ORDER BY id DESC")
        posts = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", [request.session['id']])
        userpic = cursor.fetchone()
        # pic = userpic[1]

    with connection.cursor() as cursor:
        for p in posts:
            cursor.execute("SELECT * FROM users WHERE id = %s", [p[1]])  # p[1] = user_id
            user = cursor.fetchone()   # faqat bitta user
            posts_with_users.append({
                'post': p,
                'user': user, 
            })

    return render(request, 'replies.html', {'posts': posts_with_users,   'pic': userpic})

def upload_view(request):
    if request.method == "POST" and request.FILES.get("image"):
        img = request.FILES["image"]
        
        filename = f"{int(time.time())}_{img.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        with open(file_path, "wb+") as destination:
            for chunk in img.chunks():
                destination.write(chunk)

        file_url = f"{settings.MEDIA_URL}{filename}"

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", [request.session['id']]
            )
            data = cursor.fetchone()
            pic_url = data[1]
            if pic_url:
                file_path = pic_url.replace("/media/", "")
                absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)

                if os.path.exists(absolute_path):
                    os.remove(absolute_path)

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET pic = %s WHERE id = %s", [file_url, request.session['id']]
            )

        return redirect('home')
    return render(request, 'pic-edit.html')

###############
### PROFILE ### EDITING
############### 

def change_fname(request):
    if request.method == "POST":
        content = request.POST['fname']
        mysql = """
                    UPDATE users 
                    SET first_name = %s
                    WHERE id = %s
                """
        with connection.cursor() as sql:
            sql.execute(mysql, [content, request.session['id']])
            # sql.execute("INSERT INTO posts (id, user_id, content) VALUES (NULL, %s, %s)", [request.session['id'], content])

        return redirect("home")
    return render(request, "change-firstname.html")


def logout_view(request):
    request.session.flush()
    return redirect('login')