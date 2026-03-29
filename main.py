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
from fastapi.middleware.cors import CORSMiddleware
from web import user_role, user, permission, user_detail, event

app = FastAPI()

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_role.router)
app.include_router(user.router)
app.include_router(permission.router)
app.include_router(event.router)
app.include_router(user_detail.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)