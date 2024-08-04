from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from defs import open_connect, close_connect, set_user_online, set_user_offline, create_table1, reg
from common import generate_session_token
import hashlib


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
    close_connect(connect)
    if user_row:
        set_user_online(user.username)
        session_token = generate_session_token(10)
        response = JSONResponse(content=dict(message="Login successful"))
        response.set_cookie(
            key="session_token", value=session_token, secure=True, httponly=True
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/logout")
async def logout(user: User):
    cursor, connect = open_connect()
    cursor.execute(
        "SELECT * FROM users WHERE username_db = ? AND status = 'online'",
        (user.username,)
    )
    user_row = cursor.fetchone()
    close_connect(connect)
    if user_row:
        set_user_offline(user.username)
        session_token = generate_session_token(10)
        response = JSONResponse(content={"message": "Logout successful"})
        response.set_cookie(
            key="session_token", value=session_token, secure=True, httponly=True
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/register")
async def register(user: UserCreate):
    reg(user.username, user.password, user.email)
    return JSONResponse(content={"message": "User registered successfully"})


def main():
    create_table1()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)
