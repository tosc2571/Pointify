from pydantic import BaseModel


class ShareCreate(BaseModel):
    username: str


class ShareOut(BaseModel):
    user_id: int
    username: str
