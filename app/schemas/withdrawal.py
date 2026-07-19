import datetime
from pydantic import BaseModel, ConfigDict, Field

class CreateWithdrawal(BaseModel):
    user_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)

class WithdrawalResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
