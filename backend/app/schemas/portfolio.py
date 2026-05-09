
from pydantic import BaseModel
from typing import Optional

class PortfolioBase(BaseModel):
    stock_code: str
    quantity: int
    cost_price: float

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(BaseModel):
    quantity: Optional[int] = None
    cost_price: Optional[float] = None

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    stock_id: int
    created_at: object
    updated_at: object
    
    class Config:
        orm_mode = True
