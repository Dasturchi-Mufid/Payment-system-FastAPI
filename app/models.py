from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,Enum
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .database import Base


class CardType(PyEnum):
    HUMO = "HUMO"
    UzCard = "UzCard"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)

    cards = relationship('Card', back_populates='owner')


class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, index=True)
    card_type = Column(Enum(CardType),nullable=False) 
    card_number = Column(Integer, unique=True, index=True)
    bank_name = Column(String)
    balance = Column(DECIMAL(10, 2))

    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='cards')


class Merchant(Base):
    __tablename__ = 'merchants'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_number = Column(String)
    amount_field = Column(DECIMAL(10, 2))


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(DECIMAL(10, 2))
    transaction_date = Column(String)
    device_id = Column(String)
    user_ip = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    merchant_id = Column(Integer, ForeignKey('merchants.id'))
    card_id = Column(Integer, ForeignKey('cards.id'))

    user = relationship('User')
    merchant = relationship('Merchant')
    card = relationship('Card')
