# app/schemas/notices.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Literal

# ZIP Code Model
class ViolationZipCode(BaseModel):
    zip_code: str
    state: str
    city: str
    district: str

# Violation Address Model
class ViolationAddress(BaseModel):
    street: str

# Notice Base Model
class NoticeBase(BaseModel):
    notice_id: str
    violation_date_time: datetime
    detachment: str
    violation_severity: Literal["Low", "Medium", "High"]
    notice_status: Literal["Active", "Resolved", "Expired"]
    notification_sent: bool
    entry_date: date
    expiry_date: date
    violation_description: str

# Notice shown to civilians with vehicle and location context
class CivilianNotice(NoticeBase):
    car: str
    address: str

# Notice Create Model
class NoticeCreate(NoticeBase):
    car_id: int
    violation_zip: ViolationZipCode
    violation_address: ViolationAddress
