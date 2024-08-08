from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from defs import open_connect, close_connect, login_func, logout_func, create_table1, reg, meet_func, create_table2
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="html")


class User(BaseModel):
    username: str
    password: str


class UserCreate(User):
    email: str


@app.post("/login")
async def login(username: str = Form(...),
    password: str = Form(...)):
    return login_func(username, password)


@app.post("/logout")
async def logout(username: str = Form(...)):
    logout_func(username)


@app.post("/registration")
async def register(user: UserCreate):
    cursor, conn = open_connect()
    reg(user.username, user.password, user.email, cursor)
    close_connect(conn)
    return JSONResponse(content={"message": "User registered successfully"})


class Meet(BaseModel):
    name: str
    members: str
    datetime: str


@app.post("/create_meeting")
async def create_meet(request: Request,
    name: str = Form(...),
    members: str = Form(...),
    datetime: str = Form(...),
    session_token = Cookie()):
    cursor, conn = open_connect()
    meet_func(name, members, datetime, cursor, session_token)
    close_connect(conn)
    return JSONResponse(content={"message": "Meeting created successfully"})


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/create_meeting", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("create_meeting.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/registration", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


def main():
    create_table1()
    create_table2()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)
