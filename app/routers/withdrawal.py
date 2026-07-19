from fastapi import APIRouter, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel, Field

from app.database.database import get_db
from app.schemas.withdrawal import CreateWithdrawal, WithdrawalResponse
from app.routers.auth import get_current_user, check_admin_role
from app.services import withdrawalService

router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])

class UpdateWithdrawalStatus(BaseModel):
    status: str = Field(..., pattern="^(success|failed|cancelled)$")

@router.post("", status_code=status.HTTP_201_CREATED)
def request_withdrawal(withdrawal_in: CreateWithdrawal, request: Request, db: Session = Depends(get_db)):
    """
    Creator requests a withdrawal.
    - Cannot withdraw more than available balance.
    - Only one withdrawal allowed every 24 hours.
    - Balance is deducted immediately.
    - Withdrawal is created with status = pending.
    """
    current_user = get_current_user(request, db)

    # Only CREATOR can request withdrawal for themselves
    if current_user.role != "ADMIN" and current_user.role != "CREATOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to request withdrawals."
        )

    result = withdrawalService.request_withdrawal(
        user_id=current_user.id,
        amount=withdrawal_in.amount,
        db=db
    )
    return result

@router.patch("/{withdrawal_id}")
def update_withdrawal_status(withdrawal_id: str, body: UpdateWithdrawalStatus, request: Request, db: Session = Depends(get_db)):
    """
    Admin only. Update withdrawal status to success, failed, or cancelled.
    - If failed or cancelled → amount is refunded back to user balance.
    - If success → amount stays deducted.
    """
    check_admin_role(request, db)  # Only admin can update withdrawal status

    result = withdrawalService.update_withdrawal_status(
        withdrawal_id=withdrawal_id,
        new_status=body.status,
        db=db
    )
    return result
