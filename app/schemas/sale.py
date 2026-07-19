import datetime
from pydantic import BaseModel, ConfigDict, Field

class CreateSale(BaseModel):
    user_id: str = Field(..., min_length=1)
    brand: str = Field(..., min_length=1)
    earning: float = Field(..., gt=0)

class SaleResponse(BaseModel):
    id: str
    user_id: str
    brand: str
    earning: float
    status: str
    is_advance_paid: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
