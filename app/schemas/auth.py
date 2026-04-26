# app/schemas/auth.py
from pydantic import BaseModel
from datetime import date


class CivilianAddressCreate(BaseModel):
    zip_code: str
    state: str
    city: str
    street: str
    house: str


class CivilianRegisterRequest(BaseModel):
    address: CivilianAddressCreate
    email: str
    username: str
    password: str
    phone_number: str
    licence_number: str
    state_issue: str
    last_name: str
    first_name: str
    dob: date
    height_inches: int
    weight_pounds: int
    eyes_colour: str


class CivilianResponse(BaseModel):
    driver_id: int
    email: str
    username: str
    phone_number: str
    licence_number: str
    state_issue: str
    last_name: str
    first_name: str
    dob: date
    height_inches: int
    weight_pounds: int
    eyes_colour: str

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class CivilianTokenResponse(TokenResponse):
    driver_id: int
