import sqlite3
from sqlite3 import Connection, Cursor
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import hashlib
from common import valid_email, generate_session_token
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


templates = Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)


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
            name TEXT,
            members TEXT,
            datetime DATETIME        
        )""")
    close_connect(connect)


def validate_datetime_format(datetime_str: str, format_str: str = '%Y-%m-%dT%H:%M') -> bool:
    if datetime.strptime(datetime_str, format_str):
        return True
    else:
        return False


def meet_func(name, members, dt, cookie, request):
    cursor, conn = open_connect()
    if cookie is None:
        close_connect(conn)
        context = {
        "request": request,
        "data_num": "401",
        "data" : "You're not logined",
        "src" : "create_meeting"
        }
        return templates.TemplateResponse("template_error.html", context)
    cursor.execute(
        'SELECT * FROM users WHERE session_token = ?',
        (cookie,)
    )
    organizer = cursor.fetchone()
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
    cursor.execute(
        "INSERT INTO meetings (organizer, name, members, datetime) VALUES (?, ?, ?, ?)",
        (organizer_n, name, members, dt)
    )
    close_connect(conn)
    context = {
        "request": request,
        "data": "Create meeting ",
        "src" : "create_meeting"
    }
    return templates.TemplateResponse("template.html", context)


def user_exists(username: str, email: str, cursor) -> bool:
    cursor.execute(
        'SELECT 1 FROM users WHERE username_db = ? OR email = ?',
        (username, email)
    )
    exists = cursor.fetchone() is not None
    return exists


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
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    set_user_online(username, cursor)
    create_session_token = generate_session_token(10)
    cursor.execute(
        "INSERT INTO users (username_db, password_db, email, session_token) VALUES (?, ?, ?, ?)",
        (username, hashed_password, email, create_session_token)
    )
    close_connect(conn)
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


def set_user_online(username: str, cursor):
    cursor.execute(
        "UPDATE users SET status = 'online' WHERE username_db = ?",
        (username,)
    )


def set_user_offline(cookie: str, cursor):
    cursor.execute(
        "UPDATE users SET status = 'offline' WHERE sesson_token = ?",
        (cookie,)
    )


def login_func(username, password, request):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor, connect = open_connect()
    cursor.execute(
            'SELECT * FROM users WHERE (username_db = ? AND password_db = ?) OR (email = ? AND password_db = ?)',
            (username, hashed_password, username, hashed_password)
    )
    user_row = cursor.fetchone()
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


def logout_func(cookie, request):
    if cookie is None:
        context = {
        "request": request,
        "data_num": "401",
        "data" : "You're not login",
        "src" : None
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
        create_session_token = generate_session_token(10)
        close_connect(connect)
        context = {
            "request": request,
            "data": "Login ",
            "src" : "logout"
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
            "src" : "logout"
        }
        return templates.TemplateResponse("template_error.html", context)
    

def get_data_from_db():
    cursor, conn = open_connect()
    cursor.execute("SELECT * FROM meetings")
    rows = cursor.fetchall()
    close_connect(conn)
    return rows