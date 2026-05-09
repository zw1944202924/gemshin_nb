
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.models import Stock, StockDailyData

def low_pe_high_roe_strategy(db: Session, limit: int = 20):
    """低PE高ROE策略：选择PE<30，ROE>15%的股票，按PE从小到大排序"""
    # 获取所有股票的最新PE和ROE数据
    stocks = db.query(Stock).all()
    result = []
    for stock in stocks:
        latest_data = db.query(StockDailyData).filter(
            StockDailyData.stock_id == stock.id
        ).order_by(StockDailyData.trade_date.desc()).first()
        if not latest_data or latest_data.pe is None or latest_data.pe <= 0:
            continue
        # 这里ROE暂时用PB和PE估算，后续可以接入财务数据
        roe = 100 / latest_data.pe if latest_data.pb else 0
        if latest_data.pe < 30 and roe > 15:
            result.append({
                "stock_code": stock.code,
                "stock_name": stock.name,
                "pe": latest_data.pe,
                "roe": roe,
                "price": latest_data.close,
                "market_cap": latest_data.total_market_cap
            })
    # 按PE从小到大排序
    result = sorted(result, key=lambda x: x["pe"])[:limit]
    return result

def high_dividend_strategy(db: Session, limit: int = 20):
    """高股息策略：选择股息率>3%的股票，按股息率从高到低排序"""
    # 这里暂时用低PE、低PB的蓝筹股替代，后续接入股息数据
    stocks = db.query(Stock).all()
    result = []
    for stock in stocks:
        latest_data = db.query(StockDailyData).filter(
            StockDailyData.stock_id == stock.id
        ).order_by(StockDailyData.trade_date.desc()).first()
        if not latest_data or latest_data.pe is None or latest_data.pb is None:
            continue
        if 0 < latest_data.pe < 20 and 0 < latest_data.pb < 2:
            # 估算股息率
            dividend_yield = 10 / latest_data.pe
            result.append({
                "stock_code": stock.code,
                "stock_name": stock.name,
                "pe": latest_data.pe,
                "pb": latest_data.pb,
                "dividend_yield": dividend_yield,
                "price": latest_data.close,
                "market_cap": latest_data.total_market_cap
            })
    # 按股息率从高到低排序
    result = sorted(result, key=lambda x: x["dividend_yield"], reverse=True)[:limit]
    return result

def small_cap_growth_strategy(db: Session, limit: int = 20):
    """小盘成长策略：选择市值<100亿，PE>0，营收增长>20%的股票，按市值从小到大排序"""
    stocks = db.query(Stock).all()
    result = []
    for stock in stocks:
        latest_data = db.query(StockDailyData).filter(
            StockDailyData.stock_id == stock.id
        ).order_by(StockDailyData.trade_date.desc()).first()
        if not latest_data or latest_data.total_market_cap is None or latest_data.pe is None:
            continue
        market_cap = latest_data.total_market_cap / 100000000
        if 0 < market_cap < 100 and latest_data.pe > 0:
            result.append({
                "stock_code": stock.code,
                "stock_name": stock.name,
                "market_cap": market_cap,
                "pe": latest_data.pe,
                "price": latest_data.close
            })
    # 按市值从小到大排序
    result = sorted(result, key=lambda x: x["market_cap"])[:limit]
    return result

def industry_leader_strategy(db: Session, limit: int = 20):
    """行业龙头策略：选择每个行业市值最大的前2只股票"""
    stocks = db.query(Stock).all()
    industry_map = {}
    for stock in stocks:
        if not stock.industry:
            continue
        latest_data = db.query(StockDailyData).filter(
            StockDailyData.stock_id == stock.id
        ).order_by(StockDailyData.trade_date.desc()).first()
        if not latest_data or latest_data.total_market_cap is None:
            continue
        if stock.industry not in industry_map:
            industry_map[stock.industry] = []
        industry_map[stock.industry].append({
            "stock_code": stock.code,
            "stock_name": stock.name,
            "industry": stock.industry,
            "market_cap": latest_data.total_market_cap / 100000000,
            "pe": latest_data.pe,
            "price": latest_data.close
        })
    # 每个行业取前2名，按市值排序
    result = []
    for industry, stocks in industry_map.items():
        sorted_stocks = sorted(stocks, key=lambda x: x["market_cap"], reverse=True)[:2]
        result.extend(sorted_stocks)
    # 整体按市值排序，取前limit个
    result = sorted(result, key=lambda x: x["market_cap"], reverse=True)[:limit]
    return result

# 策略映射
STRATEGY_MAP = {
    "low_pe_high_roe": low_pe_high_roe_strategy,
    "high_dividend": high_dividend_strategy,
    "small_cap_growth": small_cap_growth_strategy,
    "industry_leader": industry_leader_strategy
}

def get_strategy_list():
    """获取所有选股策略列表"""
    return [
        {"code": "low_pe_high_roe", "name": "低PE高ROE策略", "description": "选择估值低、盈利能力强的蓝筹股，适合价值投资"},
        {"code": "high_dividend", "name": "高股息策略", "description": "选择股息率高的蓝筹股，适合稳健型投资者，分红再投资收益高"},
        {"code": "small_cap_growth", "name": "小盘成长策略", "description": "选择市值小、成长潜力大的股票，弹性大，适合风险承受能力高的投资者"},
        {"code": "industry_leader", "name": "行业龙头策略", "description": "选择每个行业的龙头企业，竞争力强，业绩稳定"}
    ]

def execute_strategy(strategy_code: str, db: Session, limit: int = 20):
    """执行选股策略"""
    if strategy_code not in STRATEGY_MAP:
        return False, "策略不存在", None
    try:
        result = STRATEGY_MAP[strategy_code](db, limit)
        return True, "选股成功", result
    except Exception as e:
        return False, f"选股失败: {str(e)}", None
