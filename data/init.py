import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

conn = None
cursor = None

def get_db():
    global conn, cursor
    if conn:
        return
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/musical_band_db")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

get_db()