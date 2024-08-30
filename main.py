from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from defs import login_func, logout_func, create_table1, reg, meet_func, create_table2, get_data_from_db
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from typing import Union


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


html = Jinja2Templates(directory="html", autoescape=False, auto_reload=True)
templates = Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)
env = Environment(loader=FileSystemLoader('html'))


@app.post("/login")
async def login(request: Request, 
    username: str = Form(...),
    password: str = Form(...)):
    return login_func(username, password, request)


@app.post("/logout")
async def logout(request: Request,
    session_token = Cookie(None)):
    logout_func(session_token, request)
    context = {
        "request": request,
        "data": "Logout "
    }
    return templates.TemplateResponse("template.html", context)


@app.post("/registration", response_class=HTMLResponse)
async def registration(request: Request,
    username: str = Form(None),
    password: str = Form(None),
    email: str = Form(None)):
    reg(username, password, email, request)
    context = {
        "request": request,
        "data": "Registration "
    }
    return templates.TemplateResponse("template.html", context)


@app.post("/create_meeting", response_class=HTMLResponse)
async def create_meet(request: Request,
    name: str = Form(None),
    members: str = Form(None),
    datetime: str = Form(None),
    session_token = Cookie(None)
    ):
    return meet_func(name, members, datetime, session_token, request)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return html.TemplateResponse("index.html", {"request": request})

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


def main():
    create_table1()
    create_table2()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)


