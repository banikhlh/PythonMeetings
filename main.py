import hashlib
import random
import sqlite3
import string

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import re
import uvicorn

REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

app = FastAPI()


def get_db_connection():
    try:
        conn = sqlite3.connect("DataBase.db")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e: # это проверка просто иногда у меня в таблицу не попадает
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")


def create_table1():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username_db TEXT UNIQUE,
                    password_db TEXT,
                    email TEXT UNIQUE
                )"""
    )
    conn.commit()
    conn.close()


def valid_email(email: str) -> bool: # не знаю почему но \ все ломает
    return re.fullmatch(REGEX, email) is not None


def user_exists(username: str, email: str) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    # Используем OR в одном запросе
    c.execute(
        'SELECT 1 FROM users WHERE username_db = ? OR email = ?',
        (username, email)
    )
    # Если хотя бы одна запись найдена, возвращаем True
    exists = c.fetchone() is not None
    conn.close()
    return exists


def reg(username: str, password: str, email: str):
    if not valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if user_exists(username, email):
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username_db, password_db, email) VALUES (?, ?, ?)",
        (username, hashed_password, email),
    )
    conn.commit()
    conn.close()


def generate_session_token(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


@app.post("/login")
async def login(user: UserCreate, response: Response):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    conn = get_db_connection()
    c = conn.cursor() # сделал по другому, немного не понял тебя, но ты вроде предлагал, чтобы условно в email могло
    # входить и пароль и собственно сама почта
    c.execute(
        'SELECT * FROM users WHERE (username_db = ? AND password_db = ?) OR (email = ? AND password_db = ?)',
        (user.username, hashed_password, user.email, hashed_password)
    )
    user_row = c.fetchone()
    conn.close()

    if user_row:
        session_token = generate_session_token(10)
        response.set_cookie(key="session_token", value=session_token, secure=True, httponly=True)
        return response and JSONResponse(content=dict(message="Login successful"))
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/register")
async def register(user: UserCreate):
    reg(user.username, user.password, user.email)
    return JSONResponse(content={"message": "User registered successful"})


def main():
    create_table1()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)
