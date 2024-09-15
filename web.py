from fastapi import Request, Form, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from defs import login, logout, register, create_meeting, open_connect, get_data_from_db
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


html = Jinja2Templates(directory="html", autoescape=True, auto_reload=True)
templates = Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)


@app.post("/login")
async def web_login(request: Request, 
    username: str = Form(None),
    password: str = Form(None)):
    status_code = ""
    text, status_code = login(username, password)
    if text != "Login successful":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif text == "Login successful":
        context = {
            "request": request,
            "data": text
        }
        html_content = templates.TemplateResponse("template.html", context).body.decode('utf-8')
        response = HTMLResponse(content=html_content)
        response.set_cookie(
            key="session_token",
            value=status_code,
            secure=True,
            httponly=True
        )
        return response


@app.post("/logout")
async def web_logout(request: Request,
    session_token = Cookie(None)):
    num = ""
    txt, num = logout(session_token)
    if num != "":
        context = {
            "request": request,
            "data_num": num,
            "data" : txt,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif num == "":
        context = {
            "request": request,
            "data": txt
        }
        return templates.TemplateResponse("template.html", context)


@app.post("/registration", response_class=HTMLResponse)
async def web_registration(request: Request,
    username: str = Form(None),
    password: str = Form(None),
    email: str = Form(None)):
    num = ""
    txt, num = register(username, password, email)
    if txt != "Registration successful":
        context = {
            "request": request,
            "data_num": num,
            "data" : txt,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif txt == "Registration successful":
        context = {
            "request": request,
            "data": txt
        }
        html_content = templates.TemplateResponse("template.html", context).body.decode('utf-8')
        response = HTMLResponse(content=html_content)
        response.set_cookie(
            key="session_token",
            value=num,
            secure=True,
            httponly=True
        )
        return response


@app.post("/create_meeting", response_class=JSONResponse)
async def web_create_meet(request: Request,
    username: str = Form(None),
    members = Form(None),
    datetime: str = Form(None),
    session_token = Cookie(None)
    ):
    num = ""
    txt, num = create_meeting(username, members, datetime, session_token)
    if num != "":
        context = {
            "request": request,
            "data_num": num,
            "data" : txt,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif num == "":
        context = {
            "request": request,
            "data": txt
        }
        return templates.TemplateResponse("template.html", context)
        


@app.get("/", response_class=HTMLResponse)
async def show_main_page(request: Request,
    session_token = Cookie(None)):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE session_token = ? AND status = ?',
            (session_token, "online")
        )
        status = cursor.fetchone()
        context = {
            "status": status,
            "request": request
        }
        return html.TemplateResponse("index.html", context)

@app.get("/create_meeting", response_class=HTMLResponse)
async def show_create_meeting_page(request: Request):
    return html.TemplateResponse("create_meeting.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return html.TemplateResponse("login.html", {"request": request})

@app.get("/registration", response_class=HTMLResponse)
async def show_registration_page(request: Request):
    return html.TemplateResponse("registration.html", {"request": request})


@app.get("/meetings")
async def show_meetings_page(request: Request):
    data = get_data_from_db()
    context = {
        "request": request,
        "data" : data
        }
    return html.TemplateResponse("meetings.html", context)