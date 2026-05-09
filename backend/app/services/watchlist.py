
from sqlalchemy.orm import Session
from backend.app.models import Watchlist, Stock, StockDailyData

def get_user_watchlist(user_id: int, db: Session):
    """获取用户关注列表"""
    watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
    result = []
    for w in watchlist:
        stock = db.query(Stock).filter(Stock.id == w.stock_id).first()
        if not stock:
            continue
        # 获取最新收盘价和涨跌幅
        latest_data = db.query(StockDailyData).filter(
            StockDailyData.stock_id == stock.id
        ).order_by(StockDailyData.trade_date.desc()).limit(2).all()
        latest_price = latest_data[0].close if len(latest_data) > 0 else 0
        prev_price = latest_data[1].close if len(latest_data) > 1 else latest_price
        change_rate = (latest_price - prev_price) / prev_price * 100 if prev_price > 0 else 0
        result.append({
            "id": w.id,
            "stock_id": w.stock_id,
            "stock_code": stock.code,
            "stock_name": stock.name,
            "latest_price": latest_price,
            "change_rate": change_rate,
            "created_at": w.created_at
        })
    return result

def add_to_watchlist(user_id: int, stock_code: str, db: Session):
    """添加股票到关注列表"""
    stock = db.query(Stock).filter(Stock.code == stock_code).first()
    if not stock:
        return False, "股票不存在"
    # 检查是否已经关注
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.stock_id == stock.id
    ).first()
    if existing:
        return False, "该股票已经在关注列表中"
    watchlist = Watchlist(user_id=user_id, stock_id=stock.id)
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    return True, "添加关注成功"

def remove_from_watchlist(user_id: int, watchlist_id: int, db: Session):
    """从关注列表删除股票"""
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user_id
    ).first()
    if not watchlist:
        return False, "关注记录不存在"
    db.delete(watchlist)
    db.commit()
    return True, "取消关注成功"
