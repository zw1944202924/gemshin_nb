
import json
from typing import List, Dict
from sqlalchemy.orm import Session
from backend.app.models import Stock, StockDailyData, Portfolio
from backend.app.core.config import settings

# 系统会自动注入豆包的API配置，这里直接使用settings里的DOUBAK_API_KEY即可
DOUBAK_API_KEY = settings.doubak_api_key

def call_doubao(prompt: str) -> str:
    """调用豆包大模型接口"""
    if not DOUBAK_API_KEY:
        return "请先配置豆包API密钥"
    try:
        import requests
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {DOUBAK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"调用大模型失败，状态码：{response.status_code}，错误信息：{response.text}"
    except Exception as e:
        return f"调用大模型异常：{str(e)}"

def analyze_stock(stock_code: str, db: Session) -> Dict:
    """分析指定股票"""
    # 获取股票基本信息
    stock = db.query(Stock).filter(Stock.code == stock_code).first()
    if not stock:
        return {"success": False, "message": "股票不存在"}
    # 获取最近30个交易日的日线数据
    daily_data = db.query(StockDailyData).filter(
        StockDailyData.stock_id == stock.id
    ).order_by(StockDailyData.trade_date.desc()).limit(30).all()
    if not daily_data:
        return {"success": False, "message": "没有该股票的日线数据，请先同步数据"}
    # 构造分析数据
    data_list = []
    for d in daily_data:
        data_list.append({
            "trade_date": d.trade_date,
            "open": d.open,
            "close": d.close,
            "high": d.high,
            "low": d.low,
            "volume": d.volume,
            "turnover": d.turnover,
            "pe": d.pe,
            "pb": d.pb,
            "total_market_cap": d.total_market_cap
        })
    # 计算最近涨跌幅
    latest_close = daily_data[0].close
    prev_close = daily_data[1].close if len(daily_data) >= 2 else latest_close
    change_rate = (latest_close - prev_close) / prev_close * 100
    # 构造prompt
    prompt = f"""
你是专业的股票分析师，擅长用通俗易懂的语言给普通散户分析股票。请分析以下股票信息，给出专业的分析和建议：
股票名称：{stock.name}
股票代码：{stock_code}
所属市场：{stock.market}
最新收盘价：{latest_close}元
今日涨跌幅：{change_rate:.2f}%
市盈率(PE)：{daily_data[0].pe}
市净率(PB)：{daily_data[0].pb}
总市值：{daily_data[0].total_market_cap / 100000000:.2f}亿元
最近30个交易日的日线数据：
{json.dumps(data_list, ensure_ascii=False, indent=2)}
请按照以下结构输出分析结果，全部用中文，不要用专业术语，要通俗易懂，就像给朋友解释一样：
1. 基本面分析：从PE、PB、市值等角度分析该股票的估值水平，是高估还是低估，适合投资吗？
2. 技术面分析：从最近30个交易日的走势、成交量等角度分析该股票的短期走势，是上涨趋势、下跌趋势还是震荡？
3. 投资建议：给出明确的建议，比如买入、持有、卖出，或者观望，说明理由。
4. 风险提示：说明该股票的主要投资风险有哪些，需要注意什么？
"""
    # 调用大模型
    result = call_doubao(prompt)
    return {
        "success": True,
        "stock_name": stock.name,
        "stock_code": stock_code,
        "latest_price": latest_close,
        "change_rate": change_rate,
        "pe": daily_data[0].pe,
        "pb": daily_data[0].pb,
        "total_market_cap": daily_data[0].total_market_cap,
        "analysis_result": result
    }

def analyze_portfolio(user_id: int, db: Session) -> Dict:
    """分析用户持仓"""
    # 获取用户持仓
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    if not portfolios:
        return {"success": False, "message": "没有持仓数据"}
    total_market_value = 0
    total_cost = 0
    stock_list = []
    for p in portfolios:
        stock = db.query(Stock).filter(Stock.id == p.stock_id).first()
        if not stock:
            continue
        # 获取最新收盘价
        latest_data = db.query(StockDailyData).filter(
            StockDailyData.stock_id == stock.id
        ).order_by(StockDailyData.trade_date.desc()).first()
        if not latest_data:
            continue
        current_value = latest_data.close * p.quantity
        cost = p.cost_price * p.quantity
        profit = current_value - cost
        profit_rate = profit / cost * 100 if cost > 0 else 0
        total_market_value += current_value
        total_cost += cost
        stock_list.append({
            "code": stock.code,
            "name": stock.name,
            "quantity": p.quantity,
            "cost_price": p.cost_price,
            "latest_price": latest_data.close,
            "current_value": current_value,
            "profit": profit,
            "profit_rate": profit_rate
        })
    if total_cost == 0:
        return {"success": False, "message": "持仓成本为0"}
    total_profit = total_market_value - total_cost
    total_profit_rate = total_profit / total_cost * 100
    # 构造prompt
    prompt = f"""
你是专业的个人理财分析师，擅长给普通散户分析持仓情况，给出优化建议。请分析以下持仓数据，用通俗易懂的语言给出分析和建议，不要用专业术语：
持仓总市值：{total_market_value:.2f}元
持仓总成本：{total_cost:.2f}元
总盈亏：{total_profit:.2f}元
总收益率：{total_profit_rate:.2f}%
持仓明细：
{json.dumps(stock_list, ensure_ascii=False, indent=2)}
请按照以下结构输出分析结果：
1. 持仓整体分析：当前持仓的整体收益情况怎么样，是赚还是亏，整体配置合理吗？
2. 个股分析：逐个分析每只持仓股票的表现，哪些是盈利的，哪些是亏损的，原因可能是什么？
3. 优化建议：给出具体的持仓优化建议，比如哪些股票可以加仓，哪些可以减仓，哪些可以持有，要不要调仓换股？
4. 风险提示：当前持仓有什么风险，需要注意什么？
"""
    # 调用大模型
    result = call_doubao(prompt)
    return {
        "success": True,
        "total_market_value": total_market_value,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "total_profit_rate": total_profit_rate,
        "stock_list": stock_list,
        "analysis_result": result
    }
