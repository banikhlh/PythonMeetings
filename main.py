from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from defs import open_connect, close_connect, set_user_online, set_user_offline, create_table1, reg, meet_func
from common import generate_session_token
import hashlib
from typing import List
from datetime import datetime


app = FastAPI()


class User(BaseModel):
    username: str
    password: str


class UserCreate(User):
    email: str


@app.post("/login")
async def login(user: User):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    cursor, connect = open_connect()
    cursor.execute(
            'SELECT * FROM users WHERE (username_db = ? AND password_db = ?) OR (email = ? AND password_db = ?)',
            (user.username, hashed_password, user.username, hashed_password)
    )
    user_row = cursor.fetchone()
    if user_row:
        set_user_online(user.username, cursor)
        session_token = generate_session_token(10)
        cursor.execute(
            "UPDATE users SET session_token = ? WHERE username_db = ?",
            (session_token, user.username)
        )
        close_connect(connect)
        response = JSONResponse(content=dict(message="Login successful"))
        response.set_cookie(
            key="session_token", value=session_token, secure=True, httponly=True
        )
        return response
    else:
        close_connect(connect)
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/logout")
async def logout(user: User):
    cursor, connect = open_connect()
    cursor.execute(
        "SELECT * FROM users WHERE username_db = ? AND status = 'online'",
        (user.username,)
    )
    user_row = cursor.fetchone()
    if user_row:
        set_user_offline(user.username, cursor)
        session_token = generate_session_token(10)
        close_connect(connect)
        response = JSONResponse(content={"message": "Logout successful"})
        response.set_cookie(
            key="session_token", value=session_token, secure=True, httponly=True
        )
        return response
    else:
        close_connect(connect)
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/register")
async def register(user: UserCreate):
    reg(user.username, user.password, user.email)
    return JSONResponse(content={"message": "User registered successfully"})


class Meet(BaseModel):
    name: str
    members: List[str]
    datetime: datetime


@app.post("/create_meet")
async def create_meet(meet: Meet, request: Request):
    if meet_func(request, meet.name, meet.members, meet.datetime):
        return JSONResponse(content={"message": "Meeting created successfully"})


def main():
    create_table1()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)
