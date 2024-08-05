import sqlite3
from sqlite3 import Connection, Cursor


from fastapi import HTTPException
import hashlib
from common import valid_email


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
            status TEXT CHECK (status IN ('online', 'offline')) DEFAULT 'online'
        )""")
    close_connect(connect)


def user_exists(username: str, email: str) -> bool:
    cursor, connect = open_connect()
    cursor.execute(
        'SELECT 1 FROM users WHERE username_db = ? OR email = ?',
        (username, email)
    )
    exists = cursor.fetchone() is not None
    close_connect(connect)
    return exists


def reg(username: str, password: str, email: str):
    if not valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if user_exists(username, email):
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor, connect = open_connect()
    cursor.execute(
        "INSERT INTO users (username_db, password_db, email) VALUES (?, ?, ?)",
        (username, hashed_password, email)
    )
    close_connect(connect)


def set_user_online(username: str):
    cursor, connect = open_connect()
    cursor.execute(
        "UPDATE users SET status = 'online' WHERE username_db = ?",
        (username,)
    )
    close_connect(connect)


def set_user_offline(username: str):
    cursor, connect = open_connect()
    cursor.execute(
        "UPDATE users SET status = 'offline' WHERE username_db = ?",
        (username,)
    )
    close_connect(connect)
