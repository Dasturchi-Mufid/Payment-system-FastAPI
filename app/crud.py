from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from . import models, schemas
import random
from twilio.rest import Client

import re

# Phone number validation
def check_phone_number(number: str):
    if len(number) == 13 and number.startswith('+998') and number[1:].isdigit():
        return True
    return False

# Create user with error handling
def create_user(db: Session, user: schemas.UserCreate):
    if not check_phone_number(user.phone_number):
        return {"message": "Phone number is not valid"}
    
    try:
        db_user = models.User(username=user.username, phone_number=user.phone_number)
        db.add(db_user)
    except IntegrityError:
        db.rollback()
        return {"message": "Username or phone number already exists"}
    except DataError:
        db.rollback()
        return {"message": "Invalid data input"}
    except Exception as e:
        db.rollback()
        return {"message": f"An unexpected error occurred: {str(e)}"}
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Verify user with error handling
def verify_user(db: Session, user_id: int, verification_code: str):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user and db_user.verification_code == verification_code:
            db_user.is_verified = True
            db.commit()
            db.refresh(db_user)
            return db_user
        return {"message": "Verification failed or user not found"}
    except Exception as e:
        db.rollback()
        return {"message": f"An error occurred: {str(e)}"}

# Send verification code to user
def send_verification_code(db: Session, user_id: int):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return {"message": "User not found"}

        verification_code = str(random.randint(100000, 999999))
        db_user.verification_code = verification_code
        db.commit()

        # account_sid = 'your_account_sid'
        # auth_token = 'your_auth_token'
        # client = Client(account_sid, auth_token)
        # client.messages.create(
        #     body=f"Your verification code is {verification_code}",
        #     from_='+1234567890',
        #     to=db_user.phone_number
        # )
        
        return {"verification_code": verification_code}
    except Exception as e:
        db.rollback()
        return {"message": f"An error occurred: {str(e)}"}

# Create card for user with error handling
def create_card(db: Session, card: schemas.CardBase, user_id: int):
    try:
        db_card = models.Card(**card.dict(), user_id=user_id)
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        return db_card
    except IntegrityError:
        db.rollback()
        return {"message": "Card with this number already exists"}
    except Exception as e:
        db.rollback()
        return {"message": f"An error occurred: {str(e)}"}

# Create merchant with error handling
def create_merchant(db: Session, merchant: schemas.MerchantBase):
    try:
        db_merchant = models.Merchant(**merchant.dict())  # Ensure you call .dict() for Pydantic models
        db.add(db_merchant)
        db.commit()
        db.refresh(db_merchant)
        return db_merchant
    except IntegrityError:
        db.rollback()
        return {"message": "Merchant with this name or details already exists"}
    except Exception as e:
        db.rollback()
        return {"message": f"An error occurred: {str(e)}"}

# Create transaction with error handling
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    try:
        db_card = db.query(models.Card).filter(models.Card.id == transaction.card_id).first()
        if not db_card:
            return {"message": "Card not found"}
        if db_card.balance < transaction.amount:
            return {"message": "Insufficient balance"}

        # Deduct balance and commit the transaction
        db_card.balance -= transaction.amount
        db.commit()

        db_transaction = models.Transaction(**transaction.dict())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except IntegrityError:
        db.rollback()
        return {"message": "Transaction error. Please check card and merchant details."}
    except Exception as e:
        db.rollback()
        return {"message": f"An error occurred: {str(e)}"}
