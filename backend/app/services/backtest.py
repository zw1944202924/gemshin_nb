import pandas as pd
from sqlalchemy.orm import Session
from backend.app.models import BacktestRecord, QuantStrategy, StockDailyData, Stock
from backend.app.schemas.backtest import BacktestCreate, BacktestUpdate
from typing import List, Optional
from datetime import datetime


def get_backtest_records(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[BacktestRecord]:
    """获取用户的回测记录"""
    return db.query(BacktestRecord).filter(
        BacktestRecord.user_id == user_id
    ).order_by(BacktestRecord.created_at.desc()).offset(skip).limit(limit).all()


def get_backtest_by_id(db: Session, record_id: int, user_id: int):
    """获取指定回测记录"""
    return db.query(BacktestRecord).filter(
        BacktestRecord.id == record_id,
        BacktestRecord.user_id == user_id
    ).first()


def create_backtest(
    db: Session,
    user_id: int,
    backtest: BacktestCreate
) -> BacktestRecord:
    """创建回测记录"""
    strategy = db.query(QuantStrategy).filter(
        QuantStrategy.id == backtest.strategy_id
    ).first()

    if not strategy:
        raise ValueError("策略不存在")

    parameters = {
        "initial_capital": backtest.initial_capital,
        "commission_rate": backtest.commission_rate,
        "slippage": backtest.slippage
    }

    result = execute_backtest(
        db, backtest.strategy_id,
        backtest.start_date, backtest.end_date,
        backtest.initial_capital,
        backtest.commission_rate,
        backtest.slippage
    )

    db_record = BacktestRecord(
        user_id=user_id,
        strategy_id=backtest.strategy_id,
        name=backtest.name,
        start_date=backtest.start_date,
        end_date=backtest.end_date,
        parameters=parameters,
        result=result
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_backtest(
    db: Session,
    record_id: int,
    user_id: int,
    backtest: BacktestUpdate
) -> Optional[BacktestRecord]:
    """更新回测记录"""
    db_record = get_backtest_by_id(db, record_id, user_id)
    if not db_record:
        return None

    update_data = backtest.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "strategy_id":
            continue
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)
    return db_record


def delete_backtest(db: Session, record_id: int, user_id: int) -> bool:
    """删除回测记录"""
    db_record = get_backtest_by_id(db, record_id, user_id)
    if not db_record:
        return False

    db.delete(db_record)
    db.commit()
    return True


def execute_backtest(
    db: Session,
    strategy_id: int,
    start_date: str,
    end_date: str,
    initial_capital: float = 100000.0,
    commission_rate: float = 0.0003,
    slippage: float = 0.001
) -> dict:
    """执行回测"""
    from backend.app.services.quant import STRATEGY_MAP

    strategy = db.query(QuantStrategy).filter(
        QuantStrategy.id == strategy_id
    ).first()

    if not strategy:
        return {"error": "策略不存在"}

    try:
        success, message, stock_list = STRATEGY_MAP.get(strategy.strategy_code)(
            db, limit=10
        )

        if not success:
            return {"error": message}

        trade_records = []
        current_capital = initial_capital
        holdings = []
        daily_returns = []
        total_trades = 0

        trade_dates = db.query(StockDailyData.trade_date).filter(
            StockDailyData.trade_date >= start_date,
            StockDailyData.trade_date <= end_date
        ).distinct().order_by(StockDailyData.trade_date).all()
        trade_dates = [d[0] for d in trade_dates]

        for date in trade_dates:
            daily_value = current_capital

            if stock_list and total_trades < 5:
                for stock_info in stock_list[:3]:
                    stock = db.query(Stock).filter(
                        Stock.code == stock_info["stock_code"]
                    ).first()
                    if not stock:
                        continue

                    stock_data = db.query(StockDailyData).filter(
                        StockDailyData.stock_id == stock.id,
                        StockDailyData.trade_date == date
                    ).first()

                    if stock_data and stock_data.close:
                        price = stock_data.close * (1 + slippage)
                        shares = int(current_capital * 0.1 / price)

                        if shares > 0:
                            cost = shares * price * (1 + commission_rate)
                            if cost <= current_capital:
                                holdings.append({
                                    "stock_code": stock_info["stock_code"],
                                    "stock_name": stock_info["stock_name"],
                                    "shares": shares,
                                    "price": price,
                                    "cost": cost
                                })
                                current_capital -= cost
                                total_trades += 1

            if holdings:
                for h in holdings:
                    stock = db.query(Stock).filter(
                        Stock.code == h["stock_code"]
                    ).first()
                    if stock:
                        stock_data = db.query(StockDailyData).filter(
                            StockDailyData.stock_id == stock.id,
                            StockDailyData.trade_date == date
                        ).first()
                        if stock_data and stock_data.close:
                            value = h["shares"] * stock_data.close * (1 - commission_rate - slippage)
                            daily_value += value

            daily_return = (daily_value - initial_capital) / initial_capital
            daily_returns.append({
                "date": date,
                "value": daily_value,
                "return": daily_return
            })

        final_value = daily_returns[-1]["value"] if daily_returns else initial_capital
        total_return = (final_value - initial_capital) / initial_capital
        total_days = len(trade_dates) if trade_dates else 1
        annual_return = total_return * 250 / total_days

        max_value = initial_capital
        max_drawdown = 0
        for dr in daily_returns:
            if dr["value"] > max_value:
                max_value = dr["value"]
            drawdown = (max_value - dr["value"]) / max_value if max_value > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        returns_list = [dr["return"] for dr in daily_returns]
        avg_return = sum(returns_list) / len(returns_list) if returns_list else 0
        std_return = (sum((r - avg_return) ** 2 for r in returns_list) / len(returns_list)) ** 0.5
        sharpe_ratio = (avg_return * 250) / (std_return * (250 ** 0.5)) if std_return > 0 else 0

        win_count = sum(1 for i in range(1, len(returns_list)) if returns_list[i] > 0)
        win_rate = win_count / len(returns_list) if returns_list else 0

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "win_rate": win_rate,
            "trades": total_trades,
            "final_value": final_value,
            "holdings": holdings,
            "daily_returns": daily_returns
        }

    except Exception as e:
        return {"error": f"回测执行失败: {str(e)}"}