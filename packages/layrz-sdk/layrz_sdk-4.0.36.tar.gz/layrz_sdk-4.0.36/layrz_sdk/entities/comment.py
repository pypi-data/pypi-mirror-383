"""Comment entity"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .user import User


class Comment(BaseModel):
  """Comment entity"""

  pk: int = Field(description='Comment ID', alias='id')
  content: str = Field(description='Comment content')
  user: User | None = Field(description='Operator/User what commented the case. None if system generated')
  submitted_at: datetime = Field(description='Date of comment submission')

  metadata: dict[str, Any] = Field(
    default_factory=dict,
    description='Additional metadata associated with the comment',
  )
