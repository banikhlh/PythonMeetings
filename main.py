import hashlib
import random
import sqlite3
import string

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

app = FastAPI()


def get_db_connection():
    conn = sqlite3.connect("DataBase.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS name_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username_db TEXT UNIQUE,
                    password_db TEXT,
                    email TEXT UNIQUE
                )"""
    )
    conn.commit()
    conn.close()


create_tables()


def user_exists(username: str) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM name_table WHERE username_db = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def reg(username: str, password: str, email: str):
    if user_exists(username):
        raise HTTPException(status_code=400, detail="Username already exists")
    else:
        import re
        if re.fullmatch(regex, email):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('SELECT 1 FROM name_table WHERE email = ?', (email,))
            email1 = c.fetchone() is not None
            if email1:
                raise HTTPException(status_code=400, detail="Email already exists")
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO name_table (username_db, password_db, email) VALUES (?, ?, ?)",
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
        'SELECT * FROM name_table WHERE username_db = ? AND password_db = ? AND email = ?',
        (user.username, hashed_password, user.email)
    )
    user_row = c.fetchone()
    conn.close()

    if user_row:
        session_token = generate_session_token(10)
        response.set_cookie(
            key="session_token", value=session_token, secure=True, httponly=True
        )
        return JSONResponse(content={"message": "Login successful"})
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/register")
async def register(user: UserCreate):
    reg(user.username, user.password, user.email)
    return JSONResponse(content={"message": "User registered successfull"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
