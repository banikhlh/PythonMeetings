import sqlite3
from sqlite3 import Connection, Cursor
from fastapi import HTTPException, Request, Cookie
from fastapi.responses import JSONResponse
import hashlib
from common import valid_email, generate_session_token
from datetime import datetime
from commonmark import commonmark
from fastapi.templating import Jinja2Templates


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


def meet_func(name: str, members: str, dt: str, cookie, request):
    cursor, conn = open_connect()
    if cookie is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    cursor.execute(
        'SELECT * FROM users WHERE session_token = ?',
        (cookie,)
    )
    organizer = cursor.fetchone()
    if not organizer:
        close_connect(conn)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    organizer_n = organizer[1]
    cursor.execute(
        'SELECT * FROM meetings WHERE name = ?',
        (name,)
    )
    exists = cursor.fetchone() is not None
    if exists:
        close_connect(conn)
        raise HTTPException(status_code=400, detail="Meeting name already exists")
    if not name:
        name = f"{organizer_n}'s meeting {dt}"
    if not dt:
        close_connect(conn)
        raise HTTPException(status_code=400, detail="Datetime is required and must be in the format YYYY-MM-DD HH:MM")
    now = datetime.now()
    if not validate_datetime_format(dt):
        close_connect(conn)
        raise HTTPException(status_code=400, detail="Invalid datetime format, need YYYY-MM-DD HH:MM:SS")
    dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M')
    if now >= dt:
        close_connect(conn)
        raise HTTPException(status_code=400, detail="Datetime must be in the future")
    if not members:
        close_connect(conn)
        raise HTTPException(status_code=400, detail="People should be in the meeting")
    cursor.execute(
        "INSERT INTO meetings (organizer, name, members, datetime) VALUES (?, ?, ?, ?)",
        (organizer_n, name, members, dt)
    )
    close_connect(conn)
    context = {
        "request": request,
        "data": "Create meeting "
    }
    return templates.TemplateResponse("template.html", context)


def user_exists(username: str, email: str, cursor) -> bool:
    cursor.execute(
        'SELECT 1 FROM users WHERE username_db = ? OR email = ?',
        (username, email)
    )
    exists = cursor.fetchone() is not None
    return exists


def reg(username: str, password: str, email: str):
    cursor, conn = open_connect()
    if not valid_email(email):
        close_connect(conn)
        raise HTTPException(status_code=400, detail="Invalid email format")
    if user_exists(username, email, cursor):
        close_connect(conn)
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    set_user_online(username, cursor)
    create_session_token = generate_session_token(10)
    cursor.execute(
        "INSERT INTO users (username_db, password_db, email, session_token) VALUES (?, ?, ?, ?)",
        (username, hashed_password, email, create_session_token)
    )
    close_connect(conn)
    response = JSONResponse(content=dict(message="Registration successful"))
    response.set_cookie(
        key="last_visit",
        value=create_session_token,
        secure=True,
        httponly=True,
        samesite=None
    )
    return response


def set_user_online(username: str, cursor):
    cursor.execute(
        "UPDATE users SET status = 'online' WHERE username_db = ?",
        (username,)
    )


def set_user_offline(username: str, cursor):
    cursor.execute(
        "UPDATE users SET status = 'offline' WHERE username_db = ?",
        (username,)
    )


def login_func(username, password):
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
        response = JSONResponse(content=dict(message="Login successful"))
        response.set_cookie(
            key="session_token",
            value=create_session_token,
            secure=True,
            httponly=True
        )
        return response
    else:
        close_connect(connect)
        raise HTTPException(status_code=401, detail="Invalid credentials")


def logout_func(username):
    cursor, connect = open_connect()
    cursor.execute(
        "SELECT * FROM users WHERE username_db = ? AND status = 'online'",
        (username,)
    )
    user_row = cursor.fetchone()
    if user_row:
        set_user_offline(username, cursor)
        create_session_token = generate_session_token(10)
        close_connect(connect)
        response = JSONResponse(content=dict(message="Login successful"))
        response.set_cookie(
            key="session_token",
            value=create_session_token,
            secure=True,
            httponly=True
        )
        return response
    else:
        close_connect(connect)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

def marked_filter(text):
    return commonmark(text)