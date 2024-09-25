from sqlite3 import connect

class DataBase:
    def __init__(self, db_name='DataBase.db'):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = connect(self.db_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor

    def fetch_one(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def create_table(self, query):
        with self.conn:
            self.execute(query)

    def close(self):
        self.conn.close()