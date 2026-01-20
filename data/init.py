import os
import pg8000
from dotenv import load_dotenv

load_dotenv()

conn = None
cursor = None

def get_db():
    global conn, cursor
    if conn:
        return
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/musical_band_db")
    conn = pg8000.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))

get_db()