"""Events entities"""

from datetime import datetime
from typing import Any, Optional, Self

from pydantic import BaseModel, Field, model_validator

from .case_ignored_status import CaseIgnoredStatus
from .case_status import CaseStatus
from .comment import Comment
from .trigger import Trigger


class Case(BaseModel):
  """Case entity"""

  pk: int = Field(description='Defines the primary key of the case', alias='id')
  trigger: Trigger = Field(description='Defines the trigger of the case')
  asset_id: int = Field(description='Defines the asset ID of the case')
  comments: list[Comment] = Field(default_factory=list, description='Defines the comments of the case')
  opened_at: datetime = Field(description='Defines the date when the case was opened')
  closed_at: Optional[datetime] = Field(default=None, description='Defines the date when the case was closed')
  status: CaseStatus = Field(description='Defines the status of the case', default=CaseStatus.CLOSED)
  ignored_status: CaseIgnoredStatus = Field(
    description='Defines the ignored status of the case',
    default=CaseIgnoredStatus.NORMAL,
  )
  sequence: Optional[int | str] = Field(
    default=None,
    description='Defines the sequence of the case. This is a unique identifier for the case',
  )

  stack_count: int = Field(
    default=1,
    description='Defines how many cases are stacked together. Only applicable if the trigger allows stacking',
  )

  @model_validator(mode='before')
  def _validate_model(cls: Self, data: dict[str, Any]) -> dict[str, Any]:
    """Validate model"""
    sequence = data.get('sequence')
    if sequence is not None and isinstance(sequence, int):
      trigger = data['trigger']
      if not isinstance(trigger, Trigger):
        if pk := data.get('pk'):
          data['sequence'] = f'{trigger["code"]}/{pk}'
        elif id_ := data.get('id'):
          data['sequence'] = f'{trigger["code"]}/{id_}'
        else:
          data['sequence'] = f'{trigger["code"]}/{sequence}'
      else:
        data['sequence'] = f'{trigger.code}/{sequence}'
    else:
      data['sequence'] = f'GENERIC/{data["pk"]}'

    if stack_count := data.get('stack_count'):
      if not isinstance(stack_count, int) or stack_count < 1:
        data['stack_count'] = 1
    else:
      data['stack_count'] = 1

    return data
