from fastapi import APIRouter, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

class BalanceResponse(BaseModel):
    user_id: str
    withdrawable_balance: float

@router.get("/me", response_model=UserResponse)
def get_my_profile(request: Request, db: Session = Depends(get_db)):
    """
    Get profile of the currently logged-in user.
    """
    current_user = get_current_user(request, db)
    return current_user

@router.get("/me/balance", response_model=BalanceResponse)
def get_my_balance(request: Request, db: Session = Depends(get_db)):
    """
    Get withdrawable balance of the currently logged-in user.
    """
    current_user = get_current_user(request, db)
    return {
        "user_id": current_user.id,
        "withdrawable_balance": float(current_user.withdrawable_balance)
    }

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Get profile of a specific user.
    Creator can only access their own data.
    """
    current_user = get_current_user(request, db)

    # Only admin can access other user's data
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only access your own data."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/{user_id}/balance", response_model=BalanceResponse)
def get_user_balance_by_id(user_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Get withdrawable balance of a specific user.
    Creator can only access their own balance.
    """
    current_user = get_current_user(request, db)

    # Only admin can access other user's balance
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only access your own balance."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "user_id": user.id,
        "withdrawable_balance": float(user.withdrawable_balance)
    }
