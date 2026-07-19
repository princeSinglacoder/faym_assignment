from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.user import User


def create_sale(user_id: str, brand: str, earning: float, db: Session) -> Sale:
    """
    Create a new sale with status = pending.
    """
    # Check user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_sale = Sale(
        user_id=user_id,
        brand=brand,
        earning=earning,
        status="pending",
        is_advance_paid=False
    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale


def process_advance_payout(user_id: str, db: Session) -> dict:
    """
    Find all pending sales where advance not yet paid.
    Credit 10% of each sale's earning to user's withdrawable_balance.
    Mark is_advance_paid = True.
    """
    # Get all eligible pending sales
    eligible_sales = db.query(Sale).filter(
        Sale.user_id == user_id,
        Sale.status == "pending",
        Sale.is_advance_paid == False
    ).all()

    if not eligible_sales:
        return {
            "message": "No eligible pending sales found for advance payout",
            "sales_processed": 0,
            "total_advance_credited": 0.0
        }

    total_advance = 0.0
    for sale in eligible_sales:
        advance_amount = float(sale.earning) * 0.10
        total_advance += advance_amount

        # Credit 10% to user balance
        user = db.query(User).filter(User.id == user_id).first()
        user.withdrawable_balance = float(user.withdrawable_balance) + advance_amount

        # Mark advance as paid
        sale.is_advance_paid = True

    db.commit()

    return {
        "message": "Advance payout processed successfully",
        "sales_processed": len(eligible_sales),
        "total_advance_credited": round(total_advance, 2)
    }


def reconcile_sale(sale_id: str, new_status: str, db: Session) -> dict:
    """
    Admin reconciles a sale — sets status to approved or rejected.

    Approved:
      - Credit remaining 90% to user's withdrawable_balance

    Rejected:
      - Deduct advance (10%) from user's withdrawable_balance if balance available
    """
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )

    if sale.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sale is already '{sale.status}'. Only pending sales can be reconciled."
        )

    if new_status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'"
        )

    user = db.query(User).filter(User.id == sale.user_id).first()
    earning = float(sale.earning)
    advance_paid = earning * 0.10 if sale.is_advance_paid else 0.0

    if new_status == "approved":
        # Credit the remaining amount (earning - advance already paid)
        remaining = earning - advance_paid
        user.withdrawable_balance = float(user.withdrawable_balance) + remaining
        sale.status = "approved"
        db.commit()

        return {
            "message": "Sale approved. Remaining payout credited.",
            "sale_id": sale_id,
            "earning": earning,
            "advance_already_paid": round(advance_paid, 2),
            "remaining_credited": round(remaining, 2)
        }

    elif new_status == "rejected":
        # Deduct the advance amount already paid (if any)
        current_balance = float(user.withdrawable_balance)

        if advance_paid > 0:
            # Deduct whatever is available, no negative balance allowed
            deduction = min(advance_paid, current_balance)
            user.withdrawable_balance = current_balance - deduction
            sale.status = "rejected"
            db.commit()

            return {
                "message": "Sale rejected. Advance payout recovered.",
                "sale_id": sale_id,
                "advance_deducted": round(deduction, 2),
                "balance_remaining": round(float(user.withdrawable_balance), 2)
            }
        else:
            # No advance was paid, just reject
            sale.status = "rejected"
            db.commit()

            return {
                "message": "Sale rejected. No advance was paid, nothing to recover.",
                "sale_id": sale_id,
                "advance_deducted": 0.0
            }
