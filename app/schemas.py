from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    phone_number: str

class UserCreate(UserBase):
    pass

class UserVerify(BaseModel):
    verification_code: str

class User(UserBase):
    id: int
    is_verified: bool

    class Config:
        orm_mode = True


class CardBase(BaseModel):
    card_type: str
    card_number: str
    bank_name: str
    balance: float

class Card(CardBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class MerchantBase(BaseModel):
    name: str
    phone_number: str
    amount_field: float

class Merchant(MerchantBase):
    id: int

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    amount: float
    device_id: str
    user_ip: str

class TransactionCreate(TransactionBase):
    user_id: int
    merchant_id: int
    card_id: int

class Transaction(TransactionBase):
    id: int
    transaction_date: datetime

    class Config:
        orm_mode = True
