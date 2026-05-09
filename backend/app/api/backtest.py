from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.api.user import get_current_user
from backend.app import schemas
from backend.app.services import backtest as backtest_service

router = APIRouter()


@router.get("/", response_model=List[schemas.backtest.BacktestResponse])
def get_backtest_records(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取回测记录列表"""
    records = backtest_service.get_backtest_records(
        db, int(current_user["sub"]), skip, limit
    )
    return records


@router.get("/{record_id}", response_model=schemas.backtest.BacktestResponse)
def get_backtest_record(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定回测记录"""
    record = backtest_service.get_backtest_by_id(
        db, record_id, int(current_user["sub"])
    )
    if not record:
        raise HTTPException(status_code=404, detail="回测记录不存在")
    return record


@router.post("/", response_model=schemas.backtest.BacktestResponse, status_code=status.HTTP_201_CREATED)
def create_backtest(
    backtest: schemas.backtest.BacktestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建并执行回测"""
    try:
        record = backtest_service.create_backtest(
            db, int(current_user["sub"]), backtest
        )
        return record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回测创建失败: {str(e)}")


@router.put("/{record_id}", response_model=schemas.backtest.BacktestResponse)
def update_backtest(
    record_id: int,
    backtest: schemas.backtest.BacktestUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新回测记录"""
    updated = backtest_service.update_backtest(
        db, record_id, int(current_user["sub"]), backtest
    )
    if not updated:
        raise HTTPException(status_code=404, detail="回测记录不存在")
    return updated


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backtest(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除回测记录"""
    success = backtest_service.delete_backtest(
        db, record_id, int(current_user["sub"])
    )
    if not success:
        raise HTTPException(status_code=404, detail="回测记录不存在")