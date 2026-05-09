
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app import services
from backend.app.models import Stock, StockDailyData

router = APIRouter()

@router.get("/list")
def get_stock_list(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), keyword: str = None, db: Session = Depends(get_db)):
    """获取股票列表"""
    query = db.query(Stock)
    if keyword:
        query = query.filter((Stock.code.like(f"%{keyword}%")) | (Stock.name.like(f"%{keyword}%")))
    total = query.count()
    offset = (page - 1) * page_size
    stocks = query.offset(offset).limit(page_size).all()
    data = [{"id": s.id, "code": s.code, "name": s.name, "market": s.market, "industry": s.industry} for s in stocks]
    return {"code": 0, "message": "success", "data": {"list": data, "total": total, "page": page, "page_size": page_size}}

@router.post("/sync/list")
def sync_stock_list():
    """同步所有A股股票列表"""
    success, message = services.stock.sync_stock_list()
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message}

@router.post("/sync/{stock_code}/daily")
def sync_stock_daily_data(stock_code: str, start_date: str = None, end_date: str = None):
    """同步指定股票的日线数据"""
    success, message = services.stock.sync_stock_daily_data(stock_code, start_date, end_date)
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message}

@router.get("/{stock_code}/daily")
def get_stock_daily_data(stock_code: str, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    """获取股票日线数据"""
    stock = db.query(Stock).filter(Stock.code == stock_code).first()
    if not stock:
        return {"code": 1, "message": "股票不存在"}
    query = db.query(StockDailyData).filter(StockDailyData.stock_id == stock.id)
    if start_date:
        query = query.filter(StockDailyData.trade_date >= start_date)
    if end_date:
        query = query.filter(StockDailyData.trade_date <= end_date)
    data = query.order_by(StockDailyData.trade_date.desc()).all()
    res = [{"trade_date": d.trade_date, "open": d.open, "high": d.high, "low": d.low, "close": d.close, 
            "volume": d.volume, "turnover": d.turnover, "pe": d.pe, "pb": d.pb, "total_market_cap": d.total_market_cap} for d in data]
    return {"code": 0, "message": "success", "data": res}
