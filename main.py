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


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


html = Jinja2Templates(directory="html", autoescape=False, auto_reload=True)
templates = Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)
env = Environment(loader=FileSystemLoader('html'))


@app.post("/login")
async def login(request: Request, 
    username: str = Form(None),
    password: str = Form(None)):
    return login_func(username, password, request)


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


def main():
    create_table1()
    create_table2()


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)