from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    reset: Optional[int] = 0


class SearchRequest(BaseModel):
    limit: Optional[int] = 5
    text: str