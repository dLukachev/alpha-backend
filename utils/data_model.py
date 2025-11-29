from typing import Dict, Any

from pydantic import BaseModel


class PayloadModel(BaseModel):
    data: Dict[str, Any]
