import threading

import uvicorn

from defs import open_connect
from tg import bot
from web import app


def create_table1(cursor):
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username_db TEXT UNIQUE,
            password_db TEXT,
            email TEXT UNIQUE,
            session_token UNIQUE,
            status TEXT CHECK (status IN ('online', 'offline')) DEFAULT 'online'
        )"""
    )


def create_table2(cursor):
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organizer TEXT,
            name TEXT,
            members TEXT,
            datetime DATETIME        
        )"""
    )


def main():
    with open_connect() as conn:
        cursor = conn.cursor()
        create_table1(cursor)
        create_table2(cursor)
        conn.commit()


def start_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000)


def start_bot():
    bot.polling()


if __name__ == "__main__":
    fastapi_thread = threading.Thread(target=start_fastapi)
    bot_thread = threading.Thread(target=start_bot)

    fastapi_thread.start()
    bot_thread.start()

    fastapi_thread.join()
    bot_thread.join()
