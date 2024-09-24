from sqlite3 import connect
import hashlib
from common import valid_email, generate_session_token, validate_datetime_format
from datetime import datetime
import time


def open_connect():
   return connect('DataBase.db')


def create_room(cookie: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            text = "You aren't logged in"
            status_code = '401'
            return text, status_code
        if admin_check(cookie):
            text = "Invalid credentials"
            status_code = '401'
            return text, status_code
        cursor.execute("SELECT id FROM rooms")
        room_ids = [row[0] for row in cursor.fetchall()]
        new_room_id = None
        for i in range(1, max(room_ids, default=0) + 1):
            if i not in room_ids:
                new_room_id = i
                break
        if new_room_id is None:
            new_room_id = (max(room_ids, default=0) + 1)
        cursor.execute("INSERT INTO rooms (id) VALUES (?)", (new_room_id,))
        conn.commit()
        text = f"Room {new_room_id} created successfully"
        status_code = ''
        return text, status_code



def meeting(id_meeting: None, name, members, dt_start, dt_end, room, cookie, type):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            text = "You aren't logged"
            status_code = "401"
            return text, status_code
        if id_meeting == '' and type == 'upd':
            text = "Meeting's id shouldn't be empty"
            status_code = "400"
            return text, status_code
        cursor.execute(
            'SELECT * FROM users WHERE session_token = ?',
            (cookie,)
        )
        conn.commit()
        organizer = cursor.fetchone()
        if not organizer:
            text = "Invalid credentials"
            status_code = "401"
            return text, status_code
        organizer_a = organizer[0]
        organizer_b = organizer[1]
        if name is None:
            name = f"{organizer_b}'s meeting {dt_start}"
        cursor.execute(
            'SELECT * FROM meetings WHERE name = ? AND room = ?',
            (name, int(room),)
        )
        conn.commit()
        exists = cursor.fetchone()
        if exists:
            text = "Meeting name already exists"
            status_code = "400"
            return text, status_code
        if (dt_start is None) or (dt_end is None):
            text = "DateTime cannot be empty"
            status_code = "400"
            return text, status_code
        if validate_datetime_format(dt_start) or validate_datetime_format(dt_end):
            text = "Incorrect datetime format"
            status_code = "400"
            return text, status_code
        if dt_start == dt_end:
            text = "Start and End should be different"
            status_code = "400"
            return text, status_code
        now = datetime.now()
        dt_start = datetime.strptime(dt_start, '%Y-%m-%dT%H:%M')
        dt_end = datetime.strptime(dt_end, '%Y-%m-%dT%H:%M')
        if dt_end <= dt_start:
            text = "End should not be earlier than start"
            status_code = "400"
            return text, status_code
        if (now >= dt_start) or (now >= dt_end):
            text = "DateTime must be in future"
            status_code = "400"
            return text, status_code
        if check_datetime(dt_start, dt_end, room):
            text = "As this datetime another meeting"
            status_code = "400"
            return text, status_code
        if members is None:
            text = "People should be in the meeting"
            status_code = "400"
            return text, status_code
        if room is None:
            text = "Room cannot be empty"
            status_code = "400"
            return text
        cursor.execute(
                "SELECT * FROM rooms WHERE id = ?",
                (room,)
        )
        room_row = cursor.fetchone()
        if room_row is None:
            text = "No room with this id"
            status_code = "401"
            return text, status_code
        if type == 'crt':
            cursor.execute(
                "INSERT INTO meetings (organizer_id, name, members, dt_start, dt_end, room) VALUES (?, ?, ?, ?, ?, ?)",
                (organizer_a, name, members, dt_start, dt_end, room,)
            )
            text = "Create meeting successful"
        elif type == 'upd':
            cursor.execute(
                "UPDATE meetings SET name = ?, members = ?, dt_start = ?, dt_end = ? WHERE id = ?",
                (name, members, dt_start, dt_end, id_meeting,)
            )
            text = "Update meeting successful"
        conn.commit()
        status_code = ""
        return text, status_code
        
        
def delete_meeting(id_meeting, cookie: None, adm):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            text = "You're not logged"
            status_code = "401"
            return text, status_code
        if id_meeting is None:
            text = "Meeting's id shouldn't be empty"
            status_code = "400"
            return text, status_code
        if adm == 'yes':
            if admin_check(cookie):
                text = 'Invalid credentials'
                status_code = '400'
                return text, status_code
        elif adm == 'no':
            cursor.execute(
                "SELECT * FROM users WHERE session_token = ?",
                (cookie,)
            )
            user_row = cursor.fetchone()
            if not user_row:
                text = "Invalid credentials"
                status_code = "401"
                return text, status_code
            cursor.execute(
                "SELECT organizer_id FROM meetings WHERE id = ?",
                (id_meeting,)
            )
            org_id = cursor.fetchone()
            if org_id is None:
                text = "No meeting with that id"
                status_code = "401"
                return text, status_code
            if org_id[0] != user_row[0]:
                text = "It's not your meeting"
                status_code = "400"
                return text, status_code
        cursor.execute(
            "SELECT * FROM meetings WHERE id = ?",
            (id_meeting,)
            )
        meeting = cursor.fetchone()
        if meeting is None:
            text = "No meeting with that id"
            status_code = "401"
            return text, status_code
        cursor.execute(
            'DELETE FROM meetings WHERE id = ?',
            (id_meeting,)
        )
        conn.commit()
        text = "Delete successful"
        status_code = ""
        return text, status_code


def user_exists(username: str, email: str, cookie: None, cursor) -> bool:
    cursor.execute(
            "SELECT 1 FROM users WHERE (username_db = ? OR email = ?) AND session_token != ?",
            (username, email, cookie)
        )
    exists = cursor.fetchone() is not None
    return exists


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


def user(username, email, old_password: None, password, repeat_password, cookie: None, type):
    with open_connect() as conn:
        cursor = conn.cursor()
        if (cookie == '' or cookie is None) and type == 'upd':
            text = "You're not logged"
            status_code = "401"
            return text, status_code
        if type == 'upd':
            cursor.execute(
                "SELECT * FROM users WHERE session_token = ?",
                (cookie,)
            )
            user_row = cursor.fetchone()
        if username is None:
            text = "Username canot be empty"
            status_code = "400"
            return text, status_code
        if (password is None) or (repeat_password is None):
            text = "Password cannot be empty"
            status_code = "400"
            return text, status_code
        if password != repeat_password:
            text = "Passwords don't match"
            status_code = "400"
            return text, status_code
        if email is None:
            text = "Email cannot be empty"
            status_code = "400"
            return text, status_code
        if not valid_email(email):
            text = "Invalid email format"
            status_code = "400"
            return text, status_code
        if user_exists(username, email, "", cursor):
            text = "Username or email already exists"
            status_code = "400"
            return text, status_code
        if type == 'reg':
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            set_user_online(username, cursor)
            if cookie is None:
                cookie = generate_session_token(10)
            cursor.execute(
                "INSERT INTO users (username_db, password_db, email, session_token) VALUES (?, ?, ?, ?)",
                (username, hashed_password, email, cookie)
            )
            cursor.execute('SELECT id FROM users')
            id = cursor.fetchone()
            if id[0] == 1:
                cursor.execute(
                "UPDATE users SET admin = ? WHERE id = ?",
                ("yes", id[0],)
                )
            text = "Registration successful"
            status_code = cookie
            return text, status_code
        elif type == 'upd':
            cursor.execute(
                "SELECT * FROM users WHERE session_token = ?",
                (cookie,)
            )
            user_row = cursor.fetchone()
            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
            if user_row[2] != hashed_old_password:
                text = "Old password is incorrect"
                status_code = "400"
                return text, status_code
            if password != repeat_password:
                text = "Passwords don't match"
                status_code = "400"
                return text, status_code
            if (password is None) or (repeat_password is None):
                text = "Password cannot be empty"
                status_code = "400"
                return text, status_code
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                "UPDATE users SET username_db = ?, email = ?, password_db = ? WHERE session_token = ?",
                (username, email, hashed_password, cookie,)
            )
            text = "Update successful"
            status_code = ""
            return text, status_code
        conn.commit()


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
            text = "Login successful"
            status_code = create_session_token
            return text, status_code
        else:
            text = "Invalid credentials"
            status_code = "401"
            return text, status_code


def logout(cookie):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            text = "You're not logged"
            status_code = "401"
            return text, status_code
        cursor.execute(
            "SELECT * FROM users WHERE session_token = ? AND status = 'online'",
            (cookie,)
        )
        user_row = cursor.fetchone()
        if user_row:
            set_user_offline(cookie, cursor)
            text = "Logout successful"
            status_code = ""
            return text, status_code
        else:
            text = "Invalid credentials"
            status_code = "401"
    

def delete_user(id: None, password: None, cookie: None, adm):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            text = "You're not logged"
            status_code = "401"
            return text, status_code
        if adm == 'no' and id == '':
            if password == '' or password is None:
                text = "Password cannot be empty"
                status_code = "400"
                return text, status_code
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                'SELECT id, password_db FROM users WHERE session_token = ?',
                (cookie,)
            )
            user_row = cursor.fetchone()
            password_db = user_row[1]
            id = user_row[0]
            if password_db != hashed_password:
                text = "Password is not correct"
                status_code = "400"
                return text, status_code
        elif adm == 'yes' and password == '':
            if id == '' or id is None:
                text = 'Id cannot be empty'
                status_code = '400'
                return text, status_code
            cursor.execute(
                "SELECT * FROM users WHERE id = ? AND admin = ?",
                (id, 'no',)
            )
            user_row = cursor.fetchone()
            if not user_row:
                text = "No user with this id"
                status_code = "401"
                return text, status_code
            if admin_check(cookie):
                text = "Invalid credentials"
                status_code = "401"
                return text, status_code
        cursor.execute(
            'DELETE FROM users WHERE id = ?',
            (id,)
        )
        cursor.execute(
            'DELETE FROM meetings WHERE organizer_id = ?',
            (id,)
        )
        conn.commit()
        text = "Delete successful"
        status_code = ""
        return text, status_code
    

def profile(cookie: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE session_token = ? AND status = ?',
            (cookie, "online")
        )
        user_row = cursor.fetchone()
        if user_row is None:
            status_code = "401",
            text = "Invalid credentials",
            return text, status_code, ""
        username = user_row[1]
        email = user_row[3]
        return user_row, username, email


def get_data_from_db():
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                meetings.id, 
                users.username_db AS organizer, 
                meetings.members, 
                meetings.name, 
                meetings.dt_start,
                meetings.dt_end,
                rooms.id
            FROM meetings
            JOIN users ON meetings.organizer_id = users.id
            JOIN rooms ON meetings.room = rooms.id
        """)
        rows = cursor.fetchall()
        return rows
    

def get_room_data_from_db(room_id):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                meetings.id, 
                users.username_db AS organizer, 
                meetings.members, 
                meetings.name, 
                meetings.dt_start,
                meetings.dt_end,
                rooms.id
            FROM meetings
            JOIN users ON meetings.organizer_id = users.id
            JOIN rooms ON meetings.room = rooms.id
            WHERE meetings.room = ?
        """, (room_id,))
        rows = cursor.fetchall()
        return rows



def get_my_data_from_db(organizer_id):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                meetings.id, 
                users.username_db AS organizer, 
                meetings.members, 
                meetings.name, 
                meetings.dt_start,
                meetings.dt_end,
                meetings.room
            FROM meetings
            JOIN users ON meetings.organizer_id = users.id
            WHERE meetings.organizer_id = ?
        """, (organizer_id,))
        rows = cursor.fetchall()
        return rows
    

def get_admins():
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username_db, email FROM users WHERE admin == 'yes'")
        rows = cursor.fetchall()
        return rows
    

def check_datetime(start, end, room):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT dt_start, dt_end FROM meetings WHERE room = ?',
            (int(room),)
        )
        dt_meetings = cursor.fetchall()
        print(dt_meetings)
        for start1, end1 in dt_meetings:
            start2 = datetime.strptime(start1, "%Y-%m-%d %H:%M:%S")
            end2 = datetime.strptime(end1, "%Y-%m-%d %H:%M:%S")
            if (start <= start2 <= end) and (start2 <= start <= end2):
                return True
        return False


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
    

def check_database():
    while True:
        with open_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, dt_end FROM meetings")
            result = cursor.fetchall()
            now = datetime.now()
            for id, dt in result:
                if dt <= now:
                    cursor.execute(
                    "DELETE FROM meetings WHERE id = ?",
                    (id,)
                    )
                    conn.commit()
        time.sleep(300)


def give_admin_root(id: int, cookie: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        if owner_check(cookie):
            text = "You not owner"
            status_code = "401"
            return text, status_code
        if id is None:
            text = "Id cannot be empty"
            status_code = "400"
            return text, status_code
        cursor.execute('SELECT id FROM users')
        id_row = cursor.fetchall()
        for i in id_row:
            if id == i[0]:
                cursor.execute(
                    'UPDATE users SET admin = ? WHERE id = ?', 
                ('yes', id,)
                )
                conn.commit()
                text = "Admin appointed"
                status_code = ''
                return text, status_code
        text = "User is no finded"
        status_code = "401"
        return text, status_code


def take_admin_root(id: int, cookie: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        if owner_check(cookie):
            text = "You not owner"
            status_code = "401"
            return text, status_code
        if id is None:
            text = "Id cannot be empty"
            status_code = "400"
            return text, status_code
        cursor.execute('SELECT id FROM users')
        id_row = cursor.fetchall()
        for i in id_row:
            if id == i[0]:
                cursor.execute(
                    'UPDATE users SET admin = ? WHERE id = ?', 
                ('no', id,)
                )
                conn.commit()
                text = "Admin root taken"
                status_code = ''
                return text, status_code
        text = "User is no finded"
        status_code = "401"
        return text, status_code
    

def owner_check(cookie: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id FROM users WHERE session_token = ?',
            (cookie,)
        )
        adm = cursor.fetchone()
        if adm is None:
            return True
        elif adm[0] == 1:
            return False
        else: 
            return True
        

def admin_check(cookie: None):
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE session_token = ? AND admin = ?',
            (cookie, "yes",)
        )
        adm = cursor.fetchone()
        if adm is None:
            return True
        else:
            return False
        

def get_max_room_id():
    with open_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM rooms")
        max_id = cursor.fetchall()
        return max_id
    

def delete_room(id_room: None, password: None, cookie: None, adm):
    with open_connect() as conn:
        cursor = conn.cursor()
        if cookie is None:
            text = "You're not logged"
            status_code = "401"
            return text, status_code
        if adm == 'no':
            text = "You not admin"
            status_code = "400"
            return text, status_code
        elif adm == 'yes':
            if id_room == '' or id_room is None and password == '' or password is None:
                text = 'All fields must be filled in'
                status_code = '400'
                return text, status_code
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                'SELECT id, password_db FROM users WHERE session_token = ?',
                (cookie,)
            )
            user_row = cursor.fetchone()
            password_db = user_row[1]
            if password_db != hashed_password:
                text = "Password is not correct"
                status_code = "400"
                return text, status_code
            cursor.execute(
                "SELECT * FROM rooms WHERE id = ?",
                (id_room,)
            )
            user_row = cursor.fetchone()
            if user_row is None:
                text = "No room with this id"
                status_code = "401"
                return text, status_code
            if admin_check(cookie):
                text = "Invalid credentials"
                status_code = "401"
                return text, status_code
        cursor.execute(
            'DELETE FROM meetings WHERE room = ?',
            (id_room,)
        )
        cursor.execute(
            'DELETE FROM rooms WHERE id = ?',
            (id_room,)
        )
        conn.commit()
        text = "Delete successful"
        status_code = ""
        return text, status_code