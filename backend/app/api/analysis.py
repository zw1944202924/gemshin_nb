
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app import services

router = APIRouter()

@router.post("/stock/{stock_code}")
def analyze_stock(stock_code: str, db: Session = Depends(get_db)):
    """AI分析指定股票"""
    result = services.analysis.analyze_stock(stock_code, db)
    if not result.get("success"):
        return {"code": 1, "message": result.get("message")}
    return {"code": 0, "message": "分析成功", "data": result}

@router.post("/portfolio")
def analyze_portfolio(user_id: int = Query(1), db: Session = Depends(get_db)):
    """AI分析用户持仓"""
    result = services.analysis.analyze_portfolio(user_id, db)
    if not result.get("success"):
        return {"code": 1, "message": result.get("message")}
    return {"code": 0, "message": "分析成功", "data": result}
