from pydantic import BaseModel, Field


class CardsRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    question: str = Field(default="", max_length=2000)
