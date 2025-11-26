from pydantic import BaseModel


class PayloadModel(BaseModel):
    data: dict
