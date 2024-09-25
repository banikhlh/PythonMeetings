from defs import check_database
from sqlite3_class import DataBase
from tg import bot
from web import app
import threading
import uvicorn


def start_background_task():
    task_thread = threading.Thread(target=check_database, daemon=True)
    task_thread.start()


def create_table1(db):
    db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username_db TEXT UNIQUE,
            password_db TEXT,
            email TEXT UNIQUE,
            session_token TEXT UNIQUE,
            status TEXT CHECK (status IN ('online', 'offline')) DEFAULT 'online',
            admin TEXT CHECK (admin IN ('yes','no')) DEFAULT 'no'
        )""")


def create_table2(db):
    db.execute("""CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organizer_id INTEGER,
            name TEXT,
            members TEXT,
            dt_start TEXT,
            dt_end TEXT,
            room INTEGER,
            FOREIGN KEY(organizer_id) REFERENCES users(id),
            FOREIGN KEY(room) REFERENCES rooms(id)
        )""")
    

def create_table3(db):
    db.execute("""CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )""")


def main():
    with DataBase() as db:
        create_table1(db)
        create_table2(db)
        create_table3(db)


def start_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000)

def start_bot():
    bot.polling()

if __name__ == "__main__":
    main()
    fastapi_thread = threading.Thread(target=start_fastapi)
    bot_thread = threading.Thread(target=start_bot)
    db_check_thread = threading.Thread(target=check_database, daemon=True)

    fastapi_thread.start()
    bot_thread.start()
    db_check_thread.start()

    fastapi_thread.join()
    bot_thread.join()