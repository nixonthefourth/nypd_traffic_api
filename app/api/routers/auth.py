from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.exc import UnknownHashError
from app.schemas.auth import (
    AdminLoginRequest,
    AdminTokenResponse,
    CivilianContactUpdateRequest,
    CivilianRegisterRequest,
    CivilianResponse,
    CivilianTokenResponse,
    LoginRequest,
    TokenResponse
)
from app.core.security import (
    create_access_token,
    verify_token,
    blacklist_token,
    hash_password,
    verify_password
)
from app.database.db_raw import *

auth_router = APIRouter(prefix="/token", tags=["Authentication"])
security = HTTPBearer()


def civilian_response_from_row(row):
    return {
        "driver_id": row[0],
        "email": row[2],
        "username": row[3],
        "phone_number": row[5],
        "licence_number": row[6],
        "state_issue": row[7],
        "last_name": row[8],
        "first_name": row[9],
        "dob": row[10],
        "height_inches": row[11],
        "weight_pounds": row[12],
        "eyes_colour": row[13]
    }


def admin_response_from_row(row, username, token):
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "admin",
        "badge_number": row[0],
        "username": username,
        "last_name": row[1],
        "first_name": row[2]
    }


def validate_admin_credentials(username: str, password: str):
    return username == "officer_user" and password == "officer_password"


def require_civilian_payload(token: str):
    payload = verify_token(token)

    if payload.get("role") != "civilian" or payload.get("driver_id") is None:
        raise HTTPException(status_code=403, detail="Civilian access required")

    return payload

# POST
@auth_router.post("", response_model=TokenResponse)
def login(data: LoginRequest):

    if not validate_admin_credentials(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": data.username,
        "role": "admin"
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "admin"
    }


@auth_router.post("/admin/login", response_model=AdminTokenResponse)
def login_admin(data: AdminLoginRequest):
    if not validate_admin_credentials(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    officer = fetch_officer_by_badge(data.badge_number)

    if officer is None:
        raise HTTPException(status_code=401, detail="Invalid badge number")

    token = create_access_token({
        "sub": data.username,
        "role": "admin",
        "badge_number": officer[0]
    })

    return admin_response_from_row(officer, data.username, token)


@auth_router.post("/civilian/register", response_model=CivilianResponse, status_code=201)
def register_civilian(data: CivilianRegisterRequest):
    existing_account = civilian_account_exists(
        data.username,
        data.email,
        data.licence_number
    )

    if existing_account:
        username, email, licence_number = existing_account

        if username == data.username:
            detail = "Username is already registered"
        elif email == data.email:
            detail = "Email is already registered"
        elif licence_number == data.licence_number:
            detail = "Licence number is already registered"
        else:
            detail = "Civilian account already exists"

        raise HTTPException(status_code=409, detail=detail)

    driver_id = create_civilian_account(
        civilian=data,
        hashed_password=hash_password(data.password)
    )

    row = fetch_driver_details(driver_id)
    return civilian_response_from_row(row)


@auth_router.post("/civilian/login", response_model=CivilianTokenResponse)
def login_civilian(data: LoginRequest):
    row = fetch_civilian_by_login(data.username)

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    driver_id = row[0]
    username = row[3]
    stored_password = row[4]

    try:
        password_is_valid = verify_password(data.password, stored_password)
    except (ValueError, UnknownHashError):
        password_is_valid = data.password == stored_password

        if password_is_valid:
            update_civilian_password(driver_id, hash_password(data.password))

    if not password_is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": username,
        "driver_id": driver_id,
        "role": "civilian"
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "civilian",
        "driver_id": driver_id
    }

# GET

@auth_router.get("/civilian/me", response_model=CivilianResponse)
def get_civilian_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = require_civilian_payload(credentials.credentials)
    row = fetch_driver_details(payload["driver_id"])

    if row is None:
        raise HTTPException(status_code=404, detail="Civilian profile not found")

    return civilian_response_from_row(row)

# PUT

@auth_router.put("", response_model=TokenResponse)
def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    old_token = credentials.credentials
    payload = verify_token(old_token)

    refresh_payload = {
        key: value for key, value in payload.items()
        if key not in {"exp", "jti"}
    }

    new_token = create_access_token(refresh_payload)

    return {
        "access_token": new_token,
        "token_type": "bearer",
        "role": payload.get("role", "admin")
    }


@auth_router.put("/civilian/me", response_model=CivilianResponse)
def update_civilian_contact(
    data: CivilianContactUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = require_civilian_payload(credentials.credentials)
    driver_id = payload["driver_id"]

    if civilian_email_taken_by_other(data.email, driver_id):
        raise HTTPException(status_code=409, detail="Email is already registered")

    row = update_civilian_contact_details(
        driver_id=driver_id,
        email=data.email,
        phone_number=data.phone_number
    )

    if row is None:
        raise HTTPException(status_code=404, detail="Civilian profile not found")

    return civilian_response_from_row(row)

# DELETE

@auth_router.delete("")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    verify_token(token)

    blacklist_token(token)

    return {"message": "Successfully logged out"}
