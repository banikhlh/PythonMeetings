from sqlite3 import connect
import hashlib
from common import valid_email, generate_session_token, validate_datetime_format
from sqlite3_class import DataBase
from datetime import datetime
import time


def open_connect():
   return connect('DataBase.db')


def create_room(cookie: None):
    with DataBase() as db:
        if cookie is None:
            return "You aren't logged in", '401'
        if admin_check(cookie):
            return "Invalid credentials", '401'
        room_ids = [row[0] for row in db.fetch_all("SELECT id FROM rooms")]
        new_room_id = None
        for i in range(1, max(room_ids, default=0) + 1):
            if i not in room_ids:
                new_room_id = i
                break
        if new_room_id is None:
            new_room_id = (max(room_ids, default=0) + 1)
        db.execute("INSERT INTO rooms (id) VALUES (?)", (new_room_id,))
        return f"Room {new_room_id} created successfully", ''



def meeting(id_meeting: None, name, members, dt_start, dt_end, room, cookie, type):
    with DataBase() as db:
        if "'" in name or '"' in name or "'" in members or '"' in members:
            return "Invalid meeting name", "400"
        if cookie is None:
            return "You aren't logged", "401"
        if id_meeting == '' and type == 'upd':
            return "Meeting's id shouldn't be empty", "400"
        organizer = db.fetch_one('SELECT * FROM users WHERE session_token = ?', (cookie,))
        if not organizer:
            return "Invalid credentials", "401"
        organizer_a = organizer[0]
        organizer_b = organizer[1]
        if name is None:
            name = f"{organizer_b}'s meeting {dt_start}"
        exists = db.fetch_one('SELECT * FROM meetings WHERE name = ? AND room = ?', (name, int(room),))
        if exists:
            return "Meeting name already exists", "400"
        if (dt_start is None) or (dt_end is None):
            return "DateTime cannot be empty", "400"
        if validate_datetime_format(dt_start, '%Y-%m-%dT%H:%M') or validate_datetime_format(dt_end, '%Y-%m-%dT%H:%M'):
            return "Incorrect datetime format", "400"
        if dt_start == dt_end:
            return "Start and End should be different", "400"
        now = datetime.now()
        dt_start = datetime.strptime(dt_start, '%Y-%m-%dT%H:%M')
        dt_end = datetime.strptime(dt_end, '%Y-%m-%dT%H:%M')
        if dt_end <= dt_start:
            return "End should not be earlier than start", "400"
        if (now >= dt_start) or (now >= dt_end):
            return "DateTime must be in future", "400"
        if check_datetime(dt_start, dt_end, room):
            return "As this datetime another meeting", "400"
        if members is None:
            return "People should be in the meeting", "400"
        if room is None:
            return "Room cannot be empty", "400"
        room_row = db.fetch_one("SELECT * FROM rooms WHERE id = ?", (room,))
        if room_row is None:
            return "No room with this id", '401'
        if type == 'crt':
            db.execute("INSERT INTO meetings (organizer_id, name, members, dt_start, dt_end, room) VALUES (?, ?, ?, ?, ?, ?)", (organizer_a, name, members, dt_start, dt_end, room,))
            text = "Create meeting successful"
        elif type == 'upd':
            db.execute("UPDATE meetings SET name = ?, members = ?, dt_start = ?, dt_end = ? WHERE id = ?", (name, members, dt_start, dt_end, id_meeting,))
            text = "Update meeting successful"
        return text, ''
        
        
def delete_meeting(id_meeting, cookie: None, adm):
    with DataBase() as db:
        if cookie is None:
            return "You're not logged", "401"
        if id_meeting is None:
            return "Meeting's id shouldn't be empty", "400"
        if adm == 'yes':
            if admin_check(cookie):
                return 'Invalid credentials', '400'
        elif adm == 'no':
            user_row = db.fetch_one("SELECT * FROM users WHERE session_token = ?", (cookie,))
            if not user_row:
                return "Invalid credentials", "401"
            org_id = db.fetch_one("SELECT organizer_id FROM meetings WHERE id = ?", (id_meeting,))
            if org_id is None:
                return "No meeting with that id", "401"
            if org_id[0] != user_row[0]:
                return "It's not your meeting", "400"
        meeting = db.fetch_one("SELECT * FROM meetings WHERE id = ?", (id_meeting,))
        if meeting is None:
            return "No meeting with that id", "401"
        db.execute('DELETE FROM meetings WHERE id = ?', (id_meeting,))
        return "Delete successful", ""


def user_exists(username: str, email: str, cookie: None, db) -> bool:
    exists = db.fetch_one("SELECT 1 FROM users WHERE (username_db = ? OR email = ?) AND session_token != ?", (username, email, cookie))
    return exists


def set_user_online(username: None, db):
    db.execute("UPDATE users SET status = 'online' WHERE username_db = ? OR session_token = ?", (username, username,))


def set_user_offline(cookie: str, db):
    db.execute("UPDATE users SET status = 'offline' WHERE session_token = ?", (cookie,))


def user(username, email, old_password: None, password, repeat_password, cookie: None, type):
    with DataBase() as db:
        if '"' in username or '"' in email or "'" in password or "'" in password or "'" in username or "'" in email:
            return "Invalid username or email", "400"
        if (cookie == '' or cookie is None) and type == 'upd':
            return "You're not logged", "401"
        if type == 'upd':
            user_row = db.fetch_one("SELECT * FROM users WHERE session_token = ?", (cookie,))
        if username is None:
            return "Username canot be empty", "400"
        if (password is None) or (repeat_password is None):
            return "Password cannot be empty", "400"
        if password != repeat_password:
            return "Passwords don't match", "400"
        if email is None:
            return "Email cannot be empty", "400"
        if not valid_email(email):
            return "Invalid email format", "400"
        if user_exists(username, email, "", db):
            return "Username or email already exists", "400"
        if type == 'reg':
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            set_user_online(username, db)
            if cookie is None:
                cookie = generate_session_token(10)
            db.execute("INSERT INTO users (username_db, password_db, email, session_token) VALUES (?, ?, ?, ?)", (username, hashed_password, email, cookie))
            id = db.fetch_one('SELECT id FROM users')
            if id[0] == 1:
                db.execute("UPDATE users SET admin = ? WHERE id = ?", ("yes", id[0],))
            return "Registration successful", cookie
        elif type == 'upd':
            user_row = db.fetch_one("SELECT * FROM users WHERE session_token = ?", (cookie,))
            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
            if user_row[2] != hashed_old_password:
                return "Old password is incorrect", "400"
            if password != repeat_password:
                return "Passwords don't match", "400"
            if (password is None) or (repeat_password is None):
                return "Password cannot be empty", "400"
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            db.execute("UPDATE users SET username_db = ?, email = ?, password_db = ? WHERE session_token = ?", (username, email, hashed_password, cookie,))
            return "Update successful", ""
        

def login(username, password, create_session_token: None):
    with DataBase() as db:
        if '"' in username or "'" in password or "'" in username or '"' in password:
            return "Invalid username or password", '400'
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user_row = db.fetch_one('SELECT * FROM users WHERE (username_db = ? AND password_db = ?) OR (email = ? AND password_db = ?)', (username, hashed_password, username, hashed_password))
        if user_row:
            set_user_online(username, db)
            if create_session_token is None:
                create_session_token = generate_session_token(10)
            db.execute("UPDATE users SET session_token = ? WHERE username_db = ?", (create_session_token, username))
            return "Login successful", create_session_token
        else:
            return "Invalid credentials", "401"


def logout(cookie):
    with DataBase() as db:
        if cookie is None:
            text = "You're not logged"
            status_code = "401"
            return text, status_code
        user_row = db.fetch_one("SELECT * FROM users WHERE session_token = ?", (cookie,))
        if user_row:
            set_user_offline(cookie, db)
            return "Logout successful", ""
        else:
            return "Invalid credentials", "401"
    

def delete_user(id: None, password: None, cookie: None, adm):
    with DataBase() as db:
        if cookie is None:
            return "You're not logged", "401"
        if adm == 'no' and id == '':
            if password == '' or password is None:
                return "Password cannot be empty", "400"
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_row = db.fetch_one('SELECT id, password_db FROM users WHERE session_token = ?', (cookie,))
            password_db = user_row[1]
            id = user_row[0]
            if password_db != hashed_password:
                return "Password is not correct", "400"
        elif adm == 'yes' and password == '':
            if id == '' or id is None:
                return 'Id cannot be empty', '400'
            user_row = db.fetch_one("SELECT * FROM users WHERE id = ? AND admin = ?", (id, 'no',))
            if not user_row:
                return "No user with this id", "401"
            if admin_check(cookie):
                return "Invalid credentials", "401"
        db.execute('DELETE FROM users WHERE id = ?', (id,))
        db.execute('DELETE FROM meetings WHERE organizer_id = ?', (id,))
        return "Delete successful", ""
    

def profile(cookie: None):
    with DataBase() as db:
        user_row = db.fetch_one('SELECT * FROM users WHERE session_token = ? AND status = ?', (cookie, "online"))
        if user_row is None:
            status_code = "401",
            text = "Invalid credentials",
            return text, status_code, ""
        username = user_row[1]
        email = user_row[3]
        return user_row, username, email


def get_data_from_db():
    with DataBase() as db:
        rows = db.fetch_all("""
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
        return rows
    

def get_room_data_from_db(room_id):
    with DataBase() as db:
        rows = db.fetch_all("""
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
        return rows



def get_my_data_from_db(cookie):
    with DataBase() as db:
        organizer_id = db.fetch_one("SELECT id FROM users WHERE session_token = ?", (cookie,))
        rows = db.fetch_all("""
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
        """, (organizer_id[0],))
        return rows
    

def get_admins():
    with DataBase() as db:
        rows = db.fetch_all("SELECT id, username_db, email FROM users WHERE admin == 'yes'")
        return rows
    

def check_datetime(start, end, room):
    with DataBase() as db:
        dt_meetings = db.fetch_all('SELECT dt_start, dt_end FROM meetings WHERE room = ?', (int(room),))
        for start1, end1 in dt_meetings:
            start2 = datetime.strptime(start1, "%Y-%m-%d %H:%M:%S")
            end2 = datetime.strptime(end1, "%Y-%m-%d %H:%M:%S")
            if (start <= start2 <= end) and (start2 <= start <= end2):
                return True
        return False


def online_offline(session_token):
    with DataBase() as db:
        on_off = db.fetch_one('SELECT * FROM users WHERE session_token = ?', (session_token,))
        if on_off is None:
            return
        on_off1 = on_off[5]
        return on_off1
    

def check_database():
    while True:
        with DataBase() as db:
            result = db.fetch_all("SELECT id, dt_end FROM meetings")
            now = datetime.now()
            for id, dt in result:
                dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                if dt <= now:
                    db.execute("DELETE FROM meetings WHERE id = ?", (id,))
                    print('DELETE MEETING')
        time.sleep(300)


def give_admin_root(id: int, cookie: None):
    with DataBase() as db:
        if owner_check(cookie):
            return "You not owner", "401"
        if id is None:
            return "Id cannot be empty", "400"
        id_row = db.fetch_all('SELECT id FROM users')
        for i in id_row:
            if id == i[0]:
                db.execute('UPDATE users SET admin = ? WHERE id = ?', ('yes', id,))
                return "Admin appointed", ''
        return "User is no finded", "401"


def take_admin_root(id: int, cookie: None):
    with DataBase() as db:
        if owner_check(cookie):
            return "You not owner", "401"
        if id is None:
            return "Id cannot be empty", "400"
        id_row = db.fetch_all('SELECT id FROM users')
        for i in id_row:
            if id == i[0]:
                db.execute('UPDATE users SET admin = ? WHERE id = ?', ('no', id,))
                return "Admin root taken", ""
        return "User is no finded", "401"
    

def owner_check(cookie: None):
    with DataBase() as db:
        adm = db.fetch_one('SELECT id FROM users WHERE session_token = ?', (cookie,))
        if adm is None:
            return True
        elif adm[0] == 1:
            return False
        else: 
            return True
        

def admin_check(cookie: None):
    with DataBase() as db:
        adm = db.fetch_one('SELECT * FROM users WHERE session_token = ? AND admin = ?', (cookie, "yes",))
        if adm is None:
            return True
        else:
            return False
        

def get_max_room_id():
    with DataBase() as db:
        max_id = db.fetch_all("SELECT id FROM rooms")
        return max_id
    

def delete_room(id_room: None, password: None, cookie: None, adm):
    with DataBase() as db:
        if cookie is None:
            return "You're not logged", "401"
        if adm == 'no':
            return "You not admin", "400"
        elif adm == 'yes':
            if id_room == '' or id_room is None and password == '' or password is None:
                return 'All fields must be filled in', '400'
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_row = db.fetch_one('SELECT id, password_db FROM users WHERE session_token = ?', (cookie,))
            password_db = user_row[1]
            if password_db != hashed_password:
                return "Password is not correct", "400"
            user_row = db.fetch_one("SELECT * FROM rooms WHERE id = ?", (id_room,))
            user_row = cursor.fetchone()
            if user_row is None:
                return "No room with this id", "401"
            if admin_check(cookie):
                return "Invalid credentials", "401"
        db.execute('DELETE FROM meetings WHERE room = ?', (id_room,))
        db.execute('DELETE FROM rooms WHERE id = ?', (id_room,))
        return "Delete successful", ""