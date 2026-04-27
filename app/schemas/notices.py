# app/schemas/notices.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Literal, List

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


class DashboardOverview(BaseModel):
    total_citations: int
    active_citations: int
    citations_this_month: int
    total_drivers: int
    officer_notices_past_month: int


class DashboardCount(BaseModel):
    label: str
    count: int


class DashboardNotice(BaseModel):
    notice_id: str
    violation_date_time: datetime
    detachment: str
    district: str
    violation_severity: str
    notice_status: str
    violation_description: str


class AdminDashboardStats(BaseModel):
    overview: DashboardOverview
    violation_counts: List[DashboardCount]
    district_counts: List[DashboardCount]
    detachment_counts: List[DashboardCount]
    notices: List[DashboardNotice]

# Notice Create Model
class NoticeCreate(NoticeBase):
    car_id: int
    violation_zip: ViolationZipCode
    violation_address: ViolationAddress
