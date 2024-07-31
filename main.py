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
    conn = sqlite3.connect("DataBase.db")
    conn.row_factory = sqlite3.Row
    return conn


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


def create_table2():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username_db TEXT UNIQUE,
                    password_db TEXT,
                    email TEXT UNIQUE
                )"""
    )
    conn.commit()
    conn.close()


def valid_email(email: str) -> bool:
    return re.fullmatch(REGEX, email) is not None


def user_exists(username: str, email: str) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        'SELECT 1 FROM users WHERE username_db = ?',
        (username,)
    )
    exists1 = c.fetchone() is not None
    if exists1:
        return True
    c.execute(
        'SELECT 1 FROM users WHERE email = ?',
        (email,)
    )
    exists2 = c.fetchone() is not None
    conn.close()
    return exists2


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
    c = conn.cursor()
    c.execute(
        'SELECT * FROM users WHERE username_db = ? AND password_db = ? AND email = ?',
        (user.username, hashed_password, user.email)
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
