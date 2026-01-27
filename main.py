import logging

# Configure logging BEFORE any other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/logs.txt'),
        logging.StreamHandler()  # Also log to console
    ]
)

# Suppress watchfiles logging (used by uvicorn reload)
logging.getLogger('watchfiles.main').setLevel(logging.WARNING)

# Suppress SQLAlchemy detailed logging (queries, connection details)
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
for name in ['sqlalchemy.engine', 'sqlalchemy.pool', 'sqlalchemy.orm', 'sqlalchemy.dialects', 'sqlalchemy.engine.base']:
    logging.getLogger(name).setLevel(logging.CRITICAL)

from fastapi import FastAPI
from web import user_role

app = FastAPI()

app.include_router(user_role.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)