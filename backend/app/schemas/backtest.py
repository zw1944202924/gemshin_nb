from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class BacktestCreate(BaseModel):
    strategy_id: int
    name: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    commission_rate: float = 0.0003
    slippage: float = 0.001


class BacktestUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: Optional[float] = None
    commission_rate: Optional[float] = None
    slippage: Optional[float] = None


class BacktestResponse(BaseModel):
    id: int
    user_id: int
    strategy_id: int
    name: str
    start_date: str
    end_date: str
    parameters: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        orm_mode = True


class BacktestResult(BaseModel):
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    trades: int
    holdings: List[Dict[str, Any]]
    daily_returns: List[Dict[str, Any]]