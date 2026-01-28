from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name: str
    lastname: str
    second_lastname: str | None = None
    email: str
    password: str
    role_id: int


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy models