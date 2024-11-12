from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from . import crud, models, schemas, database

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to create a user
@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db=db, user=user)
        return db_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or phone number already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

# Route to verify a user
@app.post("/users/{user_id}/verify")
def verify_user(user_id: int, verification: schemas.UserVerify, db: Session = Depends(get_db)):
    try:
        db_user = crud.verify_user(db=db, user_id=user_id, verification_code=verification.verification_code)
        if db_user:
            return db_user
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")


@app.post("/users/{user_id}/send-verification-code")
def send_verification_code(user_id: int, db: Session = Depends(get_db)):
    try:
        verification_code = crud.send_verification_code(db=db, user_id=user_id)
        return JSONResponse(content={"message": "Verification code sent successfully"})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

# Route to create a card
@app.post("/cards/")
def create_card(card: schemas.CardBase, db: Session = Depends(get_db)):
    try:
        db_card = crud.create_card(db=db, card=card, user_id=1)
        return db_card
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card with this number already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

# Route to create a transaction
@app.post("/transactions/")
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    try:
        db_transaction = crud.create_transaction(db=db, transaction=transaction)
        if not db_transaction:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
        return db_transaction
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
