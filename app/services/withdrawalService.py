import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.withdrawal import Withdrawal
from app.models.user import User


def request_withdrawal(user_id: str, amount: float, db: Session) -> dict:
    """
    Creator requests a withdrawal.

    Rules:
    1. Cannot withdraw more than available balance.
    2. Only one withdrawal allowed every 24 hours.
    3. Deduct balance immediately and create withdrawal with status = pending.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Rule 1: Check balance is sufficient
    current_balance = float(user.withdrawable_balance)
    if amount > current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: ₹{current_balance}, Requested: ₹{amount}"
        )

    # Rule 2: Check 24-hour restriction
    if user.last_withdrawal_at:
        now = datetime.datetime.now(datetime.timezone.utc)
        last = user.last_withdrawal_at
        # Make last_withdrawal_at timezone-aware if it's not
        if last.tzinfo is None:
            last = last.replace(tzinfo=datetime.timezone.utc)
        hours_since_last = (now - last).total_seconds() / 3600
        if hours_since_last < 24:
            hours_left = round(24 - hours_since_last, 1)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Withdrawal limit: only one withdrawal per 24 hours. Try again in {hours_left} hours."
            )

    # Rule 3: Deduct balance immediately and create withdrawal
    user.withdrawable_balance = current_balance - amount
    user.last_withdrawal_at = datetime.datetime.now(datetime.timezone.utc)

    new_withdrawal = Withdrawal(
        user_id=user_id,
        amount=amount,
        status="pending"
    )

    db.add(new_withdrawal)
    db.commit()
    db.refresh(new_withdrawal)

    return {
        "message": "Withdrawal request created successfully.",
        "withdrawal_id": new_withdrawal.id,
        "amount": amount,
        "status": new_withdrawal.status,
        "balance_after_deduction": float(user.withdrawable_balance)
    }


def update_withdrawal_status(withdrawal_id: str, new_status: str, db: Session) -> dict:
    """
    Admin updates withdrawal status to 'success', 'failed', or 'cancelled'.

    If failed/cancelled → Refund the amount back to user's balance.
    If success → Keep deducted amount (nothing to do, balance already deducted).
    """
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found"
        )

    if withdrawal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Withdrawal is already '{withdrawal.status}'. Only pending withdrawals can be updated."
        )

    if new_status not in ["success", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'success', 'failed', or 'cancelled'"
        )

    user = db.query(User).filter(User.id == withdrawal.user_id).first()

    if new_status in ["failed", "cancelled"]:
        # Refund amount back to user's balance
        user.withdrawable_balance = float(user.withdrawable_balance) + float(withdrawal.amount)
        withdrawal.status = new_status
        db.commit()

        return {
            "message": f"Withdrawal {new_status}. Amount refunded to user balance.",
            "withdrawal_id": withdrawal_id,
            "amount_refunded": float(withdrawal.amount),
            "new_balance": float(user.withdrawable_balance)
        }

    elif new_status == "success":
        # Amount already deducted at request time, nothing to do
        withdrawal.status = "success"
        db.commit()

        return {
            "message": "Withdrawal marked as successful.",
            "withdrawal_id": withdrawal_id,
            "amount": float(withdrawal.amount)
        }
