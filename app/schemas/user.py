import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr
class CreateUser(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "CREATOR"
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    withdrawable_balance: float
    last_withdrawal_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)