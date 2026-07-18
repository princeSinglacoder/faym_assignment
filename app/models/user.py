import datetime
import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.sale import Sale
    from app.models.withdrawal import Withdrawal

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="CREATOR", nullable=False)  # "ADMIN", "CREATOR"
    withdrawable_balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    last_withdrawal_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="user", cascade="all, delete-orphan")
    withdrawals: Mapped[List["Withdrawal"]] = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
