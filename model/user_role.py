from pydantic import BaseModel

class UserRole(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None