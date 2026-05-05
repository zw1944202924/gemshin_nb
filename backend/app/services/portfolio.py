
from sqlalchemy.orm import Session
from backend.app.models import Portfolio, Stock, StockDailyData
from backend.app.schemas.portfolio import PortfolioCreate, PortfolioUpdate

def get_user_portfolio(user_id: int, db: Session):
    """获取用户持仓列表，带实时收益计算"""
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    result = []
    total_market_value = 0
    total_cost = 0
    total_profit = 0
    for p in portfolios:
        stock = db.query(Stock).filter(Stock.id == p.stock_id).first()
        if not stock:
            continue
        # 获取最新收盘价
        latest_data = db.query(StockDailyData).filter(
            StockDailyData.stock_id == stock.id
        ).order_by(StockDailyData.trade_date.desc()).first()
        latest_price = latest_data.close if latest_data else 0
        current_value = latest_price * p.quantity
        cost = p.cost_price * p.quantity
        profit = current_value - cost
        profit_rate = profit / cost * 100 if cost > 0 else 0
        total_market_value += current_value
        total_cost += cost
        total_profit += profit
        result.append({
            "id": p.id,
            "stock_id": p.stock_id,
            "stock_code": stock.code,
            "stock_name": stock.name,
            "quantity": p.quantity,
            "cost_price": p.cost_price,
            "latest_price": latest_price,
            "current_value": current_value,
            "profit": profit,
            "profit_rate": profit_rate,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        })
    total_profit_rate = total_profit / total_cost * 100 if total_cost > 0 else 0
    return {
        "list": result,
        "total_market_value": total_market_value,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "total_profit_rate": total_profit_rate
    }

def add_portfolio(user_id: int, portfolio_create: PortfolioCreate, db: Session):
    """添加持仓"""
    # 检查股票是否存在
    stock = db.query(Stock).filter(Stock.code == portfolio_create.stock_code).first()
    if not stock:
        return False, "股票不存在"
    # 检查是否已经持仓该股票
    existing = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.stock_id == stock.id
    ).first()
    if existing:
        # 已经持仓，更新数量和成本价
        total_quantity = existing.quantity + portfolio_create.quantity
        total_cost = existing.quantity * existing.cost_price + portfolio_create.quantity * portfolio_create.cost_price
        new_cost_price = total_cost / total_quantity
        existing.quantity = total_quantity
        existing.cost_price = new_cost_price
        db.commit()
        db.refresh(existing)
        return True, "持仓更新成功"
    else:
        # 新建持仓
        portfolio = Portfolio(
            user_id=user_id,
            stock_id=stock.id,
            quantity=portfolio_create.quantity,
            cost_price=portfolio_create.cost_price
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        return True, "持仓添加成功"

def update_portfolio(user_id: int, portfolio_id: int, portfolio_update: PortfolioUpdate, db: Session):
    """更新持仓"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    if not portfolio:
        return False, "持仓不存在"
    if portfolio_update.quantity is not None:
        portfolio.quantity = portfolio_update.quantity
    if portfolio_update.cost_price is not None:
        portfolio.cost_price = portfolio_update.cost_price
    db.commit()
    db.refresh(portfolio)
    return True, "持仓更新成功"

def delete_portfolio(user_id: int, portfolio_id: int, db: Session):
    """删除持仓"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    if not portfolio:
        return False, "持仓不存在"
    db.delete(portfolio)
    db.commit()
    return True, "持仓删除成功"
