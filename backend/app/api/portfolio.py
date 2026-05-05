
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app import services, schemas

router = APIRouter()

@router.get("/list")
def get_portfolio_list(user_id: int = Query(1), db: Session = Depends(get_db)):
    """获取用户持仓列表"""
    result = services.portfolio.get_user_portfolio(user_id, db)
    return {"code": 0, "message": "success", "data": result}

@router.post("/add")
def add_portfolio(portfolio_create: schemas.PortfolioCreate, user_id: int = Query(1), db: Session = Depends(get_db)):
    """添加持仓"""
    success, message = services.portfolio.add_portfolio(user_id, portfolio_create, db)
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message}

@router.put("/update/{portfolio_id}")
def update_portfolio(portfolio_id: int, portfolio_update: schemas.PortfolioUpdate, user_id: int = Query(1), db: Session = Depends(get_db)):
    """更新持仓"""
    success, message = services.portfolio.update_portfolio(user_id, portfolio_id, portfolio_update, db)
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message}

@router.delete("/delete/{portfolio_id}")
def delete_portfolio(portfolio_id: int, user_id: int = Query(1), db: Session = Depends(get_db)):
    """删除持仓"""
    success, message = services.portfolio.delete_portfolio(user_id, portfolio_id, db)
    if not success:
        return {"code": 1, "message": message}
    return {"code": 0, "message": message}
