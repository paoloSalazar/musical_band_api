from pydantic import BaseModel


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
