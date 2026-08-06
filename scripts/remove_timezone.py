import sys
sys.path.insert(0, '.')
from config.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE events ALTER COLUMN start_datetime TYPE TIMESTAMP WITHOUT TIME ZONE"))
    conn.execute(text("ALTER TABLE events ALTER COLUMN end_datetime TYPE TIMESTAMP WITHOUT TIME ZONE"))
    conn.commit()
print("Columns updated successfully")
