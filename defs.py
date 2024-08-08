import sqlite3
from sqlite3 import Connection, Cursor
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import hashlib
from common import valid_email, generate_session_token
from datetime import datetime


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
            name TEXT UNIQUE,
            members TEXT,
            datetime DATETIME        
        )""")
    close_connect(connect)


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
    if datetime.strptime(datetime_str, format_str):
        return True
    else:
        return False


def meet_func(request: Request, name: str, members: str, dt: str, cursor):
    cookie = get_cookie(request, cursor)
    if cookie is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    cursor.execute(
        'SELECT * FROM users WHERE session_token = ?',
        (cookie,)
    )
    organizer = cursor.fetchone()
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
    cursor.execute(
        "INSERT INTO meetings (organizer, name, members, datetime) VALUES (?, ?, ?, ?)",
        (organizer_n, name, members, dt)
    )
    response = JSONResponse(content={"message": "Meeting created successfully"}, status_code=201)
    return response


def user_exists(username: str, email: str, cursor) -> bool:
    cursor.execute(
        'SELECT 1 FROM users WHERE username_db = ? OR email = ?',
        (username, email)
    )
    exists = cursor.fetchone() is not None
    return exists


def reg(username: str, password: str, email: str, cursor):
    if not valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if user_exists(username, email, cursor):
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    set_user_online(username, cursor)
    create_session_token = generate_session_token(10)
    cursor.execute(
        "INSERT INTO users (username_db, password_db, email, session_token) VALUES (?, ?, ?, ?)",
        (username, hashed_password, email, create_session_token)
    )
    response = JSONResponse(content=dict(message="Registration successful"))
    response.set_cookie(
        key="session_token", value=create_session_token, secure=True, httponly=True
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
