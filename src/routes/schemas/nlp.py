from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    reset: Optional[int] = 0