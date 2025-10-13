from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DeliveryPeriodReadView(BaseModel):
    is_to_editable: Optional[str] = None
    address_pub_id: Optional[str] = None
    is_donation: Optional[bool] = None
    is_from_editable: Optional[str] = None
    to: Optional[str] = None
    delivery_period_pub_id: Optional[str] = None
    is_deletable: Optional[str] = None
    _from: Optional[str] = None
    is_address_editable: Optional[str] = None


DeliveryPeriodReadView.model_rebuild()
