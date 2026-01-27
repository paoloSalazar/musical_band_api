import logging
from fastapi import FastAPI
from web import user_role

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()

app.include_router(user_role.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)