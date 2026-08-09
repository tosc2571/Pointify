from pydantic import BaseModel, ConfigDict


class SubThemeCreate(BaseModel):
    title: str


class SubThemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    theme_id: int
