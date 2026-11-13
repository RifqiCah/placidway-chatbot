from datetime import datetime

from pydantic import BaseModel


class RefreshResponse(BaseModel):
    status: str
    sources: int
    chunks: int
    refreshed_at: datetime

