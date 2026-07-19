from fastapi import APIRouter, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel, Field

from app.database.database import get_db
from app.schemas.sale import CreateSale, SaleResponse
from app.routers.auth import get_current_user, check_admin_role
from app.services import saleService

router = APIRouter(prefix="/sales", tags=["Sales"])

class ReconcileRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")

@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(sale_in: CreateSale, request: Request, db: Session = Depends(get_db)):
    """
    Create a new sale. Status is always set to 'pending'.
    Only logged-in users can create sales.
    """
    current_user = get_current_user(request, db)

    # Creator can only create sales for themselves
    if current_user.role != "ADMIN" and current_user.id != sale_in.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create sales for yourself."
        )

    sale = saleService.create_sale(
        user_id=sale_in.user_id,
        brand=sale_in.brand,
        earning=sale_in.earning,
        db=db
    )
    return sale

@router.post("/advance")
def process_advance(request: Request, db: Session = Depends(get_db)):
    """
    Process advance payout for the logged-in user.
    - Finds all pending sales where advance not yet paid.
    - Credits 10% of each sale's earning to withdrawable_balance.
    - Marks is_advance_paid = True for each processed sale.
    """
    current_user = get_current_user(request, db)

    if current_user.role != "CREATOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to process advance payout."
        )

    result = saleService.process_advance_payout(
        user_id=current_user.id,
        db=db
    )
    return result

@router.patch("/{sale_id}")
def reconcile_sale(sale_id: str, body: ReconcileRequest, request: Request, db: Session = Depends(get_db)):
    """
    Admin only. Reconcile a sale by setting status to 'approved' or 'rejected'.

    Approved  → Credit remaining 90% to user's balance.
    Rejected  → Deduct advance (10%) from user's balance if available.
    """
    check_admin_role(request, db)  # Only admin can reconcile

    result = saleService.reconcile_sale(
        sale_id=sale_id,
        new_status=body.status,
        db=db
    )
    return result
