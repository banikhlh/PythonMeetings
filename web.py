from fastapi import Request, Form, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from defs import login, logout, user, profile, delete_user, meeting, delete_meeting, open_connect, get_data_from_db, get_my_data_from_db, give_admin_root, take_admin_root, get_admins, create_room, get_max_room_id, get_room_data_from_db, admin_check, delete_room
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
    text, status_code = login(username, password, None)
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
    status_code = ""
    text, status_code = logout(session_token)
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)


@app.post("/registration", response_class=HTMLResponse)
async def web_registration(request: Request,
    username: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    repeat_password: str = Form(None)
    ):
    status_code = ""
    text, status_code = user(username, email, "", password, repeat_password, None, 'reg')
    if text != "Registration successful":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif text == "Registration successful":
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
        

@app.post("/update_user", response_class=JSONResponse)
async def web_update_user(request: Request,
    username: str = Form(None),
    email: str = Form(None),
    old_password: str = Form(None),
    password: str = Form(None),
    repeat_password: str = Form(None),
    session_token: str = Cookie(None)
    ):
    status_code = ""
    text, status_code = user(username, email, old_password, password, repeat_password, session_token, "upd")
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/delete_user", response_class=JSONResponse)
async def web_delete_meet(request: Request,
    password: str = Form(None),
    session_token = Cookie(None)
    ):
    status_code = ""
    text, status_code = delete_user('', password, session_token, 'no')
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/give_admin_root", response_class=JSONResponse)
async def web_give_admin_root(request: Request,
    id: int = Form(None),
    session_token = Cookie(None)):
    status_code = ""
    text, status_code = give_admin_root(id, session_token)
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/take_admin_root", response_class=JSONResponse)
async def web_take_admin_root(request: Request,
    id: int = Form(None),
    session_token = Cookie(None)):
    status_code = ""
    text, status_code = take_admin_root(id, session_token)
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/create_room", response_class=JSONResponse)
async def web_create_room(request: Request,
    session_token = Cookie(None)
    ):
    status_code = ""
    text, status_code = create_room(session_token)
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/delete_room", response_class=JSONResponse)
async def web_delete_meet(request: Request,
    id: int = Form(None),
    password: str = Form(None),
    session_token = Cookie(None)
    ):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT admin FROM users WHERE session_token = ?",
            (session_token,)
            )
        adm = cursor.fetchone()[0]
        status_code = ""
        text, status_code = delete_room(id, password, session_token, adm)
        if status_code != "":
            context = {
                "request": request,
                "data_num": status_code,
                "data" : text,
                "src" : ""
            }
            return templates.TemplateResponse("template_error.html", context)
        elif status_code == "":
            context = {
                "request": request,
                "data": text
            }
            return templates.TemplateResponse("template.html", context)


@app.post("/create_meeting", response_class=JSONResponse)
async def web_create_meet(request: Request,
    name: str = Form(None),
    members = Form(None),
    dt_start: str = Form(None),
    dt_end: str = Form(None),
    room: int = Form(None),
    session_token = Cookie(None)
    ):
    status_code = ""
    text, status_code = meeting('', name, members, dt_start, dt_end, room, session_token, 'crt')
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/update_meeting", response_class=JSONResponse)
async def web_update_meet(request: Request,
    id_meeting: str = Form(None),
    name: str = Form(None),
    members = Form(None),
    dt_start: str = Form(None),
    dt_end: str = Form(None),
    room: int = Form(None),
    session_token = Cookie(None)
    ):
    status_code = ""
    text, status_code = meeting(id_meeting, name, members, dt_start, dt_end, room, session_token, 'upd')
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/delete_meeting", response_class=JSONResponse)
async def web_delete_meet(request: Request,
    id_meeting: str = Form(None),
    session_token = Cookie(None)
    ):
    status_code = ""
    text, status_code = delete_meeting(id_meeting, session_token, 'no')
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)


@app.post("/room")
async def show_rooms_page(request: Request,
    room: int = Form(None)):
    data = get_room_data_from_db(room)
    context = {
        "request": request,
        "data" : data
        }
    return html.TemplateResponse("meetings.html", context)


@app.post("/delete_meeting_adm", response_class=JSONResponse)
async def web_delete_meet_adm(request: Request,
    id_meeting: str = Form(None),
    session_token = Cookie(None)
    ):
    status_code = ""
    text, status_code = delete_meeting(id_meeting, session_token, 'yes')
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)
    

@app.post("/delete_user_adm", response_class=JSONResponse)
async def web_delete_user_adm(request: Request,
    id: str = Form(None),
    session_token = Cookie(None)
    ):
    status_code = ""
    text, status_code = delete_user(id, '', session_token, 'yes')
    if status_code != "":
        context = {
            "request": request,
            "data_num": status_code,
            "data" : text,
            "src" : ""
        }
        return templates.TemplateResponse("template_error.html", context)
    elif status_code == "":
        context = {
            "request": request,
            "data": text
        }
        return templates.TemplateResponse("template.html", context)


@app.get("/", response_class=HTMLResponse)
async def show_main_page(request: Request,
    session_token = Cookie(None)):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, admin FROM users WHERE session_token = ? AND status = ?',
            (session_token, "online")
        )
        status = cursor.fetchone()
        if status is None:
            context = {
                "status": False,
                "request": request
            }
        else:
            context = {
                "id": status[0],
                "status": True,
                "admin": status[1],
                "request": request
            }
        return html.TemplateResponse("index.html", context)
    

@app.get("/profile", response_class=JSONResponse)
async def show_profile_page(request: Request,
    session_token = Cookie(None)):
    user_row, username, email = profile(session_token)
    if email == "":
        context = {
        "request": request,
        "data_num": "401",
        "data" : "Invalid credentials",
        }
        return templates.TemplateResponse("template_error.html", context)
    context = {
        "status": user_row,
        "username": username,
        "email": email,
        "request": request
    }
    return html.TemplateResponse("profile.html", context)


@app.get("/login", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return html.TemplateResponse("login.html", {"request": request})


@app.get("/registration", response_class=HTMLResponse)
async def show_registration_page(request: Request):
    return html.TemplateResponse("user.html", {"request": request, "type": 'reg'})


@app.get("/update_user")
async def show_update_user_page(request: Request):
    return html.TemplateResponse("user.html", {"request": request, "type": 'upd'})


@app.get("/delete_user")
async def show_delete_user_page(request: Request):
    return html.TemplateResponse("delete_user.html", {"request": request, "adm": 'no'})


@app.get("/give_admin_root")
async def show_give_admin_root_page(request: Request):
    return html.TemplateResponse("give_admin_root.html", {"request": request})


@app.get("/take_admin_root")
async def show_take_admin_root_page(request: Request):
    return html.TemplateResponse("take_admin_root.html", {"request": request})


@app.get("/admins")
async def show_admins_page(request: Request):
    data = get_admins()
    context = {
        "request": request,
        "data" : data
        }
    return html.TemplateResponse("admins.html", context)


@app.get("/meetings")
async def show_meetings_page(request: Request):
    data = get_data_from_db()
    context = {
        "request": request,
        "data" : data
        }
    return html.TemplateResponse("meetings.html", context)


@app.get("/my_meetings")
async def show_my_meetings_page(request: Request,
    session_token = Cookie(None)):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE session_token = ?",
            (session_token,)
        )
        user = cursor.fetchone()
        user_id = user[0]
        status = get_my_data_from_db(user_id)
        context = {
            "data": status,
            "request": request
        }
        return html.TemplateResponse("my_meetings.html", context)
    

@app.get("/create_meeting", response_class=HTMLResponse)
async def show_create_meeting_page(request: Request):
    return html.TemplateResponse("meeting.html", {"request": request, "type": 'crt'})


@app.get("/update_meeting", response_class=JSONResponse)
async def show_update_meeting_page(request: Request):
    return html.TemplateResponse("meeting.html", {"request": request, "type": 'upd'})


@app.get("/delete_meeting", response_class=JSONResponse)
async def show_delete_meeting_page(request: Request):
    return html.TemplateResponse("del_meeting.html", {"request": request, "adm": 'no'})


@app.get("/rooms", response_class=HTMLResponse)
async def rooms(request: Request):
    max_id = get_max_room_id()
    return html.TemplateResponse("rooms.html", {"request": request, "count": max_id})
        

@app.get("/delete_meeting_adm", response_class=JSONResponse)
async def show_delete_meeting_adm_page(request: Request):
    return html.TemplateResponse("del_meeting.html", {"request": request, "adm": 'yes'})


@app.get("/delete_user_adm", response_class=JSONResponse)
async def show_delete_user_adm_page(request: Request):
    return html.TemplateResponse("del_user.html", {"request": request, "adm": 'yes'})


@app.get("/admin_panel", response_class=JSONResponse)
async def show_admin_panel_page(request: Request,
    session_token = Cookie(None)):
    adm = admin_check(session_token)
    return html.TemplateResponse("admin.html", {"request": request, "adm": adm})


@app.get("/delete_room")
async def show_take_admin_root_page(request: Request):
    return html.TemplateResponse("del_room.html", {"request": request})