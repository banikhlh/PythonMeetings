from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from defs import open_connect, close_connect, login_func, logout_func, create_table1, reg, meet_func, create_table2
from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import typing
from starlette.requests import Request
from starlette.testclient import TestClient


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


html = Jinja2Templates(directory="html", autoescape=False, auto_reload=True)
templates = Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)
env = Environment(loader=FileSystemLoader('html'))


class User(BaseModel):
    username: str
    password: str


class UserCreate(User):
    email: str


@app.post("/login")
async def login(request: Request, 
    username: str = Form(...),
    password: str = Form(...)):
    login_func(username, password)
    context = {
        "request": request,
        "data": "Login "
    }
    return templates.TemplateResponse("template.html", context)


@app.post("/logout")
async def logout(request: Request,
    username: str = Form(...)):
    logout_func(username)
    context = {
        "request": request,
        "data": "Logout "
    }
    return templates.TemplateResponse("template.html", context)


@app.post("/registration", response_class=HTMLResponse)
async def registration(request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...)):
    reg(username, password, email)
    context = {
        "request": request,
        "data": "Registration "
    }
    return templates.TemplateResponse("template.html", context)


@app.post("/create_meeting", response_class=HTMLResponse)
async def create_meet(request: Request,
    name: str = Form(),
    members: str = Form(),
    datetime: str = Form(),
    session_token = Cookie()
    ):
    return meet_func(name, members, datetime, session_token, request)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return html.TemplateResponse("index.html", {"request": request})

@app.get("/create_meeting", response_class=HTMLResponse)
async def read_root_cm(request: Request):
    return html.TemplateResponse("create_meeting.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def read_root_l(request: Request):
    return html.TemplateResponse("login.html", {"request": request})

@app.get("/registration", response_class=HTMLResponse)
async def read_root_r(request: Request):
    return html.TemplateResponse("registration.html", {"request": request})


def main():
    create_table1()
    create_table2()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)


