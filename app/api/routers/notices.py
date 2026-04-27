# app/api/routers/notices.py
# Imports
from fastapi import HTTPException, APIRouter, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.database.db_raw import *
from app.schemas.notices import *
from app.core.security import require_admin, verify_token

# Defines the Router
notices_router = APIRouter(
prefix="/notices",
tags=["Notices"])

security = HTTPBearer()

"""GET"""


def dashboard_count_from_row(row):
    return {
        "label": row[0],
        "count": row[1]
    }


def dashboard_notice_from_row(row):
    return {
        "notice_id": row[0],
        "violation_date_time": row[1],
        "detachment": row[2],
        "district": row[3],
        "violation_severity": row[4],
        "notice_status": row[5],
        "violation_description": row[6]
    }


def admin_notice_from_row(row):
    return {
        "notice_id": row[0],
        "car_id": row[1],
        "violation_date_time": row[2],
        "detachment": row[3],
        "violation_severity": row[4],
        "notice_status": row[5],
        "notification_sent": row[6],
        "entry_date": row[7],
        "expiry_date": row[8],
        "violation_description": row[9],
        "driver": row[10],
        "licence_number": row[11],
        "car": row[12],
        "vin": row[13],
        "licence_plate": row[14],
        "address": row[15],
        "street": row[16],
        "zip_code": row[17],
        "city": row[18],
        "state": row[19],
        "district": row[20],
        "officer": row[21],
        "badge_number": row[22]
    }


@notices_router.get("/admin/dashboard", response_model=AdminDashboardStats, status_code=status.HTTP_200_OK)
async def get_admin_dashboard_stats(
    district: str | None = Query(default=None),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token_payload = require_admin(verify_token(credentials.credentials))
    badge_number = token_payload.get("badge_number")

    if badge_number is None:
        raise HTTPException(status_code=403, detail="Admin badge is required")

    stats = fetch_admin_dashboard_stats(
        badge_number=badge_number,
        district=district,
        sort_order=sort_order
    )

    return {
        "overview": stats["overview"],
        "violation_counts": [
            dashboard_count_from_row(row) for row in stats["violation_counts"]
        ],
        "district_counts": [
            dashboard_count_from_row(row) for row in stats["district_counts"]
        ],
        "detachment_counts": [
            dashboard_count_from_row(row) for row in stats["detachment_counts"]
        ],
        "notices": [
            dashboard_notice_from_row(row) for row in stats["notices"]
        ]
    }


@notices_router.get("/admin", response_model=List[AdminNotice], status_code=status.HTTP_200_OK)
async def get_admin_notices(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    require_admin(verify_token(credentials.credentials))
    rows = fetch_admin_notices()

    return [admin_notice_from_row(row) for row in rows]


# Get Driver's Notice Details by ID
@notices_router.get("/{driver_id}", response_model=List[CivilianNotice], status_code=status.HTTP_200_OK)
async def get_driver_notice(
    driver_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token_payload = verify_token(credentials.credentials)

    if token_payload.get("role") == "civilian" and token_payload.get("driver_id") != driver_id:
        raise HTTPException(status_code=403, detail="Cannot access another driver's notices")

    # Perform the Operation
    rows = fetch_driver_notices(driver_id)

    # Notice Details
    notices = []

    for row in rows:
        notices.append({
            "notice_id": row[0],
            "violation_date_time": row[1],
            "detachment": row[2],
            "violation_severity": row[3],
            "notice_status": row[4],
            "notification_sent": row[5],
            "entry_date": row[6],
            "expiry_date": row[7],
            "violation_description": row[8],
            "car": row[9],
            "address": row[10]
        })

    # Return the Results
    return notices

"""POST"""

# Create New Notice
@notices_router.post("", response_model=AdminNotice, status_code=status.HTTP_200_OK)
async def insert_new_notice(
    notice: NoticeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token_payload = require_admin(verify_token(credentials.credentials))
    badge_number = token_payload.get("badge_number")

    if badge_number is None:
        raise HTTPException(status_code=403, detail="Admin badge is required")

    try:
        notice_id = create_notice(notice, notice.violation_zip, notice.violation_address)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    if notice_id is None:
        raise HTTPException(
            status_code=404,
            detail="Car does not exist. Cannot issue notice."
        )

    create_notice_action(notice_id, badge_number)
    row = fetch_admin_notice(notice_id)

    return admin_notice_from_row(row)

"""DELETE"""

# Delete Notice by ID
@notices_router.delete("/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_notice(
    notice_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    require_admin(verify_token(credentials.credentials))

    deleted = delete_notice(notice_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    return {"message": f"Notice {notice_id} deleted successfully"}

"""PUT"""

# Fully Updates Notice Details
@notices_router.put("/{notice_id}", response_model=AdminNotice, status_code=status.HTTP_201_CREATED)
async def update_existing_notice(
    notice_id: str,
    payload: NoticeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    require_admin(verify_token(credentials.credentials))

    updated_notice = update_notice(notice_id, payload)

    if updated_notice is None:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    row = fetch_admin_notice(notice_id)

    return admin_notice_from_row(row)
