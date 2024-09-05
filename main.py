<<<<<<< HEAD
from fastapi import FastAPI, Request, Form, Cookie, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from defs import close_connect, login_func, logout_func, create_table1, open_connect, reg, meet_func, create_table2, get_data_from_db
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
import json
=======
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from defs import open_connect, close_connect, set_user_online, set_user_offline, create_table1, reg, meet_func, create_table2
from common import generate_session_token
import hashlib
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


html = Jinja2Templates(directory="html", autoescape=False, auto_reload=True)
templates = Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)
env = Environment(loader=FileSystemLoader('html'))


@app.post("/login")
<<<<<<< HEAD
async def login(request: Request, 
    username: str = Form(...),
    password: str = Form(...)):
    return login_func(username, password, request)
=======
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
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993


@app.post("/logout")
async def logout(request: Request,
    response: Response,
    session_token = Cookie(None)):
    return logout_func(session_token, request, response)


@app.post("/registration", response_class=HTMLResponse)
async def registration(request: Request,
    username: str = Form(None),
    password: str = Form(None),
    email: str = Form(None)):
    return reg(username, password, email, request)


@app.post("/create_meeting", response_class=JSONResponse)
async def create_meet(request: Request,
    name: str = Form(None),
    members = Form(None),
    datetime: str = Form(None),
    session_token = Cookie(None)
    ):
    return meet_func(name, members, datetime, session_token, request)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request,
    session_token = Cookie(None)):
    cursor, conn = open_connect()
    cursor.execute(
        'SELECT * FROM users WHERE session_token = ? AND status = ?',
        (session_token, "online")
    )
<<<<<<< HEAD
    status = cursor.fetchone()
    context = {
        "status": status,
        "request": request
    }
    close_connect(conn)
    return html.TemplateResponse("index.html", context)

@app.get("/create_meeting", response_class=HTMLResponse)
async def read_root_1(request: Request):
    return html.TemplateResponse("create_meeting.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def read_root_2(request: Request):
    return html.TemplateResponse("login.html", {"request": request})

@app.get("/registration", response_class=HTMLResponse)
async def read_root_3(request: Request):
    return html.TemplateResponse("registration.html", {"request": request})


@app.get("/meetings")
async def read_table(request: Request):
    data = get_data_from_db()
    context = {
        "request": request,
        "data" : data
        }
    return html.TemplateResponse("meetings.html", context)
=======
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
    cursor, conn = open_connect()
    reg(user.username, user.password, user.email, cursor)
    close_connect(conn)
    return JSONResponse(content={"message": "User registered successfully"})
>>>>>>> 25a7876cf225a7d44148e336ac6c9a643c5f3993


class Meet(BaseModel):
    name: str
    members: str
    datetime: str


@app.post("/create_meet")
async def create_meet(meet: Meet, request: Request):
    cursor, conn = open_connect()
    meet_func(request, meet.name, meet.members, meet.datetime, cursor)
    close_connect(conn)


def main():
    create_table1()
    create_table2()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)


