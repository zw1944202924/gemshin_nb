
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app import services

router = APIRouter()

@router.get("/list")
def get_watchlist(user_id: int = Query(1), db: Session = Depends(get_db)):
    """获取用户关注列表"""
    result = services.watchlist.get_user_watchlist(user_id, db)
    return {"code": 0, "message": "success", "data": result}

@router.post("/add")
def add_to_watchlist(stock_code: str, user_id: int = Query(1), db: Session = Depends(get_db)):
    """添加股票到关注列表"""
    success, message = services.watchlist.add_to_watchlist(user_id, stock_code, db)
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message}

@router.delete("/delete/{watchlist_id}")
def remove_from_watchlist(watchlist_id: int, user_id: int = Query(1), db: Session = Depends(get_db)):
    """从关注列表删除股票"""
    success, message = services.watchlist.remove_from_watchlist(user_id, watchlist_id, db)
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message}
