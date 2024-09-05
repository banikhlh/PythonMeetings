import sqlite3
from sqlite3 import Connection, Cursor
<<<<<<< HEAD
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import hashlib
from common import valid_email, generate_session_token
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


templates = Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)
=======
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import hashlib
from common import valid_email, generate_session_token
from datetime import datetime
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993


def get_db_connection():
    try:
        conn = sqlite3.connect("DataBase.db")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")


def open_connect() -> (Cursor | Connection):
    conn = get_db_connection()
    cursor = conn.cursor()
    return cursor, conn


def close_connect(conn: Connection):
    conn.commit()
    conn.close()


def create_table1():
    cursor, connect = open_connect()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username_db TEXT UNIQUE,
            password_db TEXT,
            email TEXT UNIQUE,
            session_token UNIQUE,
            status TEXT CHECK (status IN ('online', 'offline')) DEFAULT 'online'
        )""")
    close_connect(connect)


def create_table2():
    cursor, connect = open_connect()
    cursor.execute("""CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organizer TEXT,
<<<<<<< HEAD
            name TEXT,
=======
            name TEXT UNIQUE,
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
            members TEXT,
            datetime DATETIME        
        )""")
    close_connect(connect)


<<<<<<< HEAD
def validate_datetime_format(datetime_str: str, format_str: str = '%Y-%m-%dT%H:%M') -> bool:
=======
def get_cookie(request: Request, cursor):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token provided")
    cursor.execute(
        'SELECT 1 FROM users WHERE session_token = ?',
        (session_token,)
    )
    exists = cursor.fetchone() is not None
    if not exists:
        return HTTPException(status_code=401, detail="Invalid session token")
    else:
        return session_token


def validate_datetime_format(datetime_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> bool:
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
    if datetime.strptime(datetime_str, format_str):
        return True
    else:
        return False


<<<<<<< HEAD
def meet_func(name, members, dt, cookie, request):
    cursor, conn = open_connect()
    if cookie is None:
        close_connect(conn)
        context = {
        "request": request,
        "data_num": "401",
        "data" : "You're not logged",
        "src" : "create_meeting"
        }
        return templates.TemplateResponse("template_error.html", context)
=======
def meet_func(request: Request, name: str, members: str, dt: str, cursor):
    cookie = get_cookie(request, cursor)
    if cookie is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
    cursor.execute(
        'SELECT * FROM users WHERE session_token = ?',
        (cookie,)
    )
    organizer = cursor.fetchone()
<<<<<<< HEAD
    if not organizer:
        close_connect(conn)
        context = {
        "request": request,
        "data_num": "401",
        "data" : "Invalid credentials",
        "src" : "create_meeting"
        }
        return templates.TemplateResponse("template_error.html", context)
    organizer_n = organizer[1]
    if name is None:
        name = f"{organizer_n}'s meeting {dt}"
    cursor.execute(
        'SELECT * FROM meetings WHERE name = ?',
        (name,)
    )
    exists = cursor.fetchone()
    if exists:
        close_connect(conn)
        context = {
        "request": request,
        "data_num": "400",
        "data" : "Meeting name already exists",
        "src" : "create_meeting"
        }
        return templates.TemplateResponse("template_error.html", context)
    if dt is None:
        close_connect(conn)
        context = {
        "request": request,
        "data_num": "400",
        "data" : "DateTime cannot be empty",
        "src" : "create_meeting"
        }
        return templates.TemplateResponse("template_error.html", context)
    now = datetime.now()
    dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M')
    if now >= dt:
        close_connect(conn)
        context = {
        "request": request,
        "data_num": "400",
        "data" : "Datetime must be in future",
        "src" : "create_meeting"
        }
        return templates.TemplateResponse("template_error.html", context)
    if members is None:
        close_connect(conn)
        context = {
        "request": request,
        "data_num": "400",
        "data" : "People should be in the meeting",
        "src" : "create_meeting"
        }
        return templates.TemplateResponse("template_error.html", context)
=======
    organizer_n = organizer['username_db']
    if not organizer:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not name:
        name = f"{organizer_n}'s meeting {dt}"
    if not dt:
        raise HTTPException(status_code=400,detail="Datetime is required and must be in the format YYYY-MM-DD HH:MM:SS")
    now = datetime.now()
    if not validate_datetime_format(dt):
        raise HTTPException(status_code=400, detail="Invalid datetime format, need YYYY-MM-DD HH:MM:SS")
    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    if now >= dt:
        raise HTTPException(status_code=400, detail="Datetime must be in the future")
    if not members:
        raise HTTPException(status_code=400, detail="People should be in the meeting")
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
    cursor.execute(
        "INSERT INTO meetings (organizer, name, members, datetime) VALUES (?, ?, ?, ?)",
        (organizer_n, name, members, dt)
    )
<<<<<<< HEAD
    close_connect(conn)
    context = {
        "request": request,
        "data": "Create meeting ",
        "src" : "create_meeting"
    }
    return templates.TemplateResponse("template.html", context)
=======
    response = JSONResponse(content={"message": "Meeting created successfully"}, status_code=201)
    return response
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993


def user_exists(username: str, email: str, cursor) -> bool:
    cursor.execute(
        'SELECT 1 FROM users WHERE username_db = ? OR email = ?',
        (username, email)
    )
    exists = cursor.fetchone() is not None
    return exists


<<<<<<< HEAD
def reg(username, password, email, request):
    if username is None:
        context = {
            "request": request,
            "data_num": "400",
            "data": "Username cannot be empty",
            "src" : "registration"
        }
        return templates.TemplateResponse("template_error.html", context)
    if password is None:
        context = {
            "request": request,
            "data_num": "400",
            "data": "Password cannot be empty",
            "src" : "registration"
        }
        return templates.TemplateResponse("template_error.html", context)
    if email is None:
        context = {
            "request": request,
            "data_num": "400",
            "data": "Email cannot be empty",
            "src" : "registration"
        }
        return templates.TemplateResponse("template_error.html", context)
    cursor, conn = open_connect()
    if not valid_email(email):
        close_connect(conn)
        context = {
            "request": request,
            "data_num": "400",
            "data": "Invalid email format",
            "src" : "registration"
        }
        return templates.TemplateResponse("template_error.html", context)
    if user_exists(username, email, cursor):
        close_connect(conn)
        context = {
            "request": request,
            "data_num": "400",
            "data": "Username or email already exists",
            "src" : "registration"
        }
        return templates.TemplateResponse("template_error.html", context)
=======
def reg(username: str, password: str, email: str, cursor):
    if not valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if user_exists(username, email, cursor):
        raise HTTPException(status_code=400, detail="Username or email already exists")
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    set_user_online(username, cursor)
    create_session_token = generate_session_token(10)
    cursor.execute(
        "INSERT INTO users (username_db, password_db, email, session_token) VALUES (?, ?, ?, ?)",
        (username, hashed_password, email, create_session_token)
    )
<<<<<<< HEAD
    close_connect(conn)
    context = {
        "request": request,
        "data": "Registration "
    }
    html_content = templates.TemplateResponse("template.html", context).body.decode('utf-8')
    response = HTMLResponse(content=html_content)
    response.set_cookie(
        key="session_token",
        value=create_session_token,
        secure=True,
        httponly=True
=======
    response = JSONResponse(content=dict(message="Registration successful"))
    response.set_cookie(
        key="session_token", value=create_session_token, secure=True, httponly=True
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
    )
    return response


def set_user_online(username: str, cursor):
    cursor.execute(
        "UPDATE users SET status = 'online' WHERE username_db = ?",
        (username,)
    )


<<<<<<< HEAD
def set_user_offline(cookie: str, cursor):
    cursor.execute(
        "UPDATE users SET status = 'offline' WHERE session_token = ?",
        (cookie,)
    )


def login_func(username, password, request):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor, connect = open_connect()
=======
def set_user_offline(username: str, cursor):
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
    cursor.execute(
            'SELECT * FROM users WHERE (username_db = ? AND password_db = ?) OR (email = ? AND password_db = ?)',
            (username, hashed_password, username, hashed_password)
    )
<<<<<<< HEAD
    user_row = cursor.fetchone()
    cursor.execute(
            'SELECT * FROM users WHERE username_db = ? AND status = ?',
            (username, "online")
    )
    user_status = cursor.fetchone()
    if user_status:
        close_connect(connect)
        context = {
        "request": request,
        "data_num": "401",
        "data" : "You already logged",
        "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    if user_row:
        set_user_online(username, cursor)
        create_session_token = generate_session_token(10)
        cursor.execute(
            "UPDATE users SET session_token = ? WHERE username_db = ?",
            (create_session_token, username)
        )
        close_connect(connect)
        context = {
            "request": request,
            "data": "Login ",
            "src" : "login"
        }
        html_content = templates.TemplateResponse("template.html", context).body.decode('utf-8')
        response = HTMLResponse(content=html_content)
        response.set_cookie(
            key="session_token",
            value=create_session_token,
            secure=True,
            httponly=True
        )
        return response
    else:
        close_connect(connect)
        context = {
        "request": request,
        "data_num": "401",
        "data" : "Invalid credentials",
        "src" : "login"
        }
        return templates.TemplateResponse("template_error.html", context)


def logout_func(cookie, request, response):
    if cookie is None:
        context = {
        "request": request,
        "data_num": "401",
        "data" : "You're not logged",
        "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    cursor, connect = open_connect()
    cursor.execute(
        "SELECT * FROM users WHERE session_token = ? AND status = 'online'",
        (cookie,)
    )
    user_row = cursor.fetchone()
    if user_row:
        set_user_offline(cookie, cursor)
        close_connect(connect)
        context = {
            "request": request,
            "data": "Logout ",
            "src" : ""
        }
        html_content = templates.TemplateResponse("template.html", context).body.decode('utf-8')
        response = HTMLResponse(content=html_content)
        return response
    else:
        close_connect(connect)
        context = {
            "request": request,
            "data_num": "401",
            "data" : "Invalid credentials",
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    

def get_data_from_db():
    cursor, conn = open_connect()
    cursor.execute("SELECT * FROM meetings")
    rows = cursor.fetchall()
    close_connect(conn)
    return rows
=======
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993
