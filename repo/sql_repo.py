import string

import psycopg2


class SqlRepo:
    def __init__(self):
        # logger = logging.getLogger(current_thread().name)
        self.connection = psycopg2.connect(
            host="localhost",
            database="testdb",
            user="sriramrao",
            password="",
            port=5433)
        self.cursor = None

    def fetch_entity(self, sql: string):
        cursor = self.get_cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        self.complete_cursor(cursor)
        return result

    def fetch_entities(self, sql: string):
        cursor = self.get_cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        self.complete_cursor(cursor)
        return result

    def execute(self, command: string) -> int:
        cursor = self.get_cursor()
        cursor.execute(command)
        row_count = cursor.rowcount
        if self.cursor is None:
            self.connection.commit()
        self.complete_cursor(cursor)
        return row_count

    def begin_transaction(self):
        self.cursor = self.connection.cursor()

    def commit_transaction(self):
        self.connection.commit()
        self.cursor.close()
        self.cursor = None

    def rollback_transaction(self):
        self.connection.rollback()
        self.cursor.close()
        self.cursor = None

    def get_cursor(self):
        if self.cursor is None:
            return self.connection.cursor()
        return self.cursor

    def complete_cursor(self, cursor):
        if self.cursor is not None:
            return
        cursor.close()
