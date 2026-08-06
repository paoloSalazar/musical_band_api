import pg8000
from config.database import DATABASE_URL_PG8000

conn = None
cursor = None

def get_db():
    global conn, cursor
    if conn:
        return
    DATABASE_URL = DATABASE_URL_PG8000
    conn = pg8000.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))

get_db()