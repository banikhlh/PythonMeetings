from sqlite3 import connect
import hashlib
from common import valid_email, generate_session_token
from datetime import datetime


def open_connect():
   return connect('DataBase.db')


def validate_datetime_format(datetime_str: str, format_str: str = '%Y-%m-%dT%H:%M') -> bool:
    if datetime.strptime(datetime_str, format_str):
        return True
    else:
        return False


def create_meeting(name, members, dt, cookie):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            txt = "You aren't logged"
            num = "401"
            return txt, num
        cursor.execute(
            'SELECT * FROM users WHERE session_token = ?',
            (cookie,)
        )
        conn.commit()
        organizer = cursor.fetchone()
        if not organizer:
            txt = "Invalid credentials"
            num = "401"
            return txt, num
        organizer_n = organizer[1]
        if name is None:
            name = f"{organizer_n}'s meeting {dt}"
        cursor.execute(
            'SELECT * FROM meetings WHERE name = ?',
            (name,)
        )
        conn.commit()
        exists = cursor.fetchone()
        if exists:
            txt = "Meeting name already exists"
            num = "400"
            return txt, num
        if dt is None:
            txt = "DateTime cannot be empty"
            num = "400"
            return txt, num
        now = datetime.now()
        dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M')
        if now >= dt:
            txt = "DateTime must be in future"
            num = "400"
            return txt, num
        if members is None:
            txt = "People should be in the meeting"
            num = "400"
            return txt, num
        cursor.execute(
            "INSERT INTO meetings (organizer, name, members, datetime) VALUES (?, ?, ?, ?)",
            (organizer_n, name, members, dt)
        )
        conn.commit()
        txt = "Create meeting successful"
        num = ""
        return txt, num


def user_exists(username: str, email: str, cursor) -> bool:
    cursor.execute(
        'SELECT 1 FROM users WHERE username_db = ? OR email = ?',
        (username, email)
    )
    exists = cursor.fetchone() is not None
    return exists


def register(username, password, email, create_session_token: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        if username is None:
            txt = "Username canot be empty"
            num = "400"
            return txt, num
        if password is None:
            txt = "Password cannot be empty"
            num = "400"
            return txt, num
        if email is None:
            txt = "Email cannot be empty"
            num = "400"
            return txt, num
        if not valid_email(email):
            txt = "Invalid email format"
            num = "400"
            return txt, num
        if user_exists(username, email, cursor):
            txt = "Username or email already exists"
            num = "400"
            return txt, num
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        set_user_online(username, cursor)
        if create_session_token is None:
            create_session_token = generate_session_token(10)
        cursor.execute(
            "INSERT INTO users (username_db, password_db, email, session_token) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, create_session_token)
        )
        conn.commit()
        txt = "Registration successful"
        num = create_session_token
        return txt, num


def set_user_online(username: None, cursor):
    cursor.execute(
        "UPDATE users SET status = 'online' WHERE username_db = ? OR session_token = ?",
        (username, username,)
    )


def set_user_offline(cookie: str, cursor):
    cursor.execute(
        "UPDATE users SET status = 'offline' WHERE session_token = ?",
        (cookie,)
    )


def login(username, password, create_session_token: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
                'SELECT * FROM users WHERE (username_db = ? AND password_db = ?) OR (email = ? AND password_db = ?)',
                (username, hashed_password, username, hashed_password)
        )
        user_row = cursor.fetchone()
        if user_row:
            set_user_online(username, cursor)
            if create_session_token is None:
                create_session_token = generate_session_token(10)
            cursor.execute(
                "UPDATE users SET session_token = ? WHERE username_db = ?",
                (create_session_token, username)
            )
            txt = "Login successful"
            num = create_session_token
            return txt, num
        else:
            txt = "Invalid credentials"
            num = "401"
            return txt, num


def logout(cookie):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            txt = "You're not logged"
            num = "401"
            return txt, num
        cursor.execute(
            "SELECT * FROM users WHERE session_token = ? AND status = 'online'",
            (cookie,)
        )
        user_row = cursor.fetchone()
        if user_row:
            set_user_offline(cookie, cursor)
            txt = "Logout successful"
            num = ""
            return txt, num
        else:
            txt = "Invalid credentials"
            num = "401"
    

def get_data_from_db():
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM meetings")
        rows = cursor.fetchall()
        return rows


def online_offline(session_token):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE session_token = ?',
            (session_token,)
        )
        on_off = cursor.fetchone()
        if on_off is None:
            return
        on_off1 = on_off[5]
        return on_off1


def users_txt():
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        text_output = "\n".join([", ".join(map(str, row)) for row in rows])
        return text_output