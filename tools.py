from main import get_db_connection


def drop_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(f"DROP TABLE IF EXISTS users")
    conn.close()