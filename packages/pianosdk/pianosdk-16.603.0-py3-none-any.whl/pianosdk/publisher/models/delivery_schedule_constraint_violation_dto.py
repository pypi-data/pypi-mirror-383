from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.period_reference_dto import PeriodReferenceDTO
from typing import List


class DeliveryScheduleConstraintViolationDTO(BaseModel):
    conflicting_periods_references: Optional['List[PeriodReferenceDTO]'] = None
    constraint_violation_code: Optional[str] = None
    message: Optional[str] = None
    target_period_reference: Optional['PeriodReferenceDTO'] = None


DeliveryScheduleConstraintViolationDTO.model_rebuild()
