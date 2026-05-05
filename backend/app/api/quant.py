
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app import services

router = APIRouter()

@router.get("/strategies")
def get_strategy_list():
    """获取所有选股策略列表"""
    result = services.quant.get_strategy_list()
    return {"code": 0, "message": "success", "data": result}

@router.post("/execute/{strategy_code}")
def execute_strategy(strategy_code: str, limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """执行选股策略"""
    success, message, data = services.quant.execute_strategy(strategy_code, db, limit)
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message, "data": data}
