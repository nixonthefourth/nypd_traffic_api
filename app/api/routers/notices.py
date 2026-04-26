# app/api/routers/notices.py
# Imports
from fastapi import HTTPException, APIRouter, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.database.db_raw import *
from app.schemas.notices import *
from app.core.security import verify_token

# Defines the Router
notices_router = APIRouter(
prefix="/notices",
tags=["Notices"])

security = HTTPBearer()

"""GET"""

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
@notices_router.post("", response_model=NoticeBase, status_code=status.HTTP_200_OK)
async def insert_new_notice(
    notice: NoticeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    verify_token(credentials.credentials)

    notice_id = create_notice(notice, notice.violation_zip, notice.violation_address)

    if notice_id is None:
        raise HTTPException(
            status_code=404,
            detail="Car does not exist. Cannot issue notice."
        )

    return {
        "notice_id": notice.notice_id,
        "violation_date_time": notice.violation_date_time,
        "detachment": notice.detachment,
        "violation_severity": notice.violation_severity,
        "notice_status": notice.notice_status,
        "notification_sent": notice.notification_sent,
        "entry_date": notice.entry_date,
        "expiry_date": notice.expiry_date,
        "violation_description": notice.violation_description
    }

"""DELETE"""

# Delete Notice by ID
@notices_router.delete("/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_notice(
    notice_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    verify_token(credentials.credentials)

    deleted = delete_notice(notice_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    return {"message": f"Notice {notice_id} deleted successfully"}

"""PUT"""

# Fully Updates Notice Details
@notices_router.put("/{notice_id}", response_model=NoticeBase, status_code=status.HTTP_201_CREATED)
async def update_existing_notice(
    notice_id: str,
    payload: NoticeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    verify_token(credentials.credentials)

    row = update_notice(notice_id, payload)

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    return {
        "notice_id": row[0],
        "violation_date_time": row[1],
        "detachment": row[2],
        "violation_severity": row[3],
        "notice_status": row[4],
        "notification_sent": row[5],
        "entry_date": row[6],
        "expiry_date": row[7],
        "violation_description": row[8]
    }
