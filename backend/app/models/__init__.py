
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True)
    doubao_api_key = Column(String(255))  # 豆包API密钥
    feishu_webhook = Column(String(255))  # 飞书通知webhook
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Stock(Base):
    """股票基本信息表"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # 股票代码
    name = Column(String(100), nullable=False)  # 股票名称
    market = Column(String(20), nullable=False)  # 市场：SH/SZ/BJ
    industry = Column(String(100))  # 所属行业
    listing_date = Column(String(20))  # 上市日期
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class StockDailyData(Base):
    """股票日线数据表"""
    __tablename__ = "stock_daily_data"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    trade_date = Column(String(20), nullable=False, index=True)  # 交易日期
    open = Column(Float)  # 开盘价
    high = Column(Float)  # 最高价
    low = Column(Float)  # 最低价
    close = Column(Float)  # 收盘价
    volume = Column(Float)  # 成交量
    turnover = Column(Float)  # 成交额
    pe = Column(Float)  # 市盈率
    pb = Column(Float)  # 市净率
    total_market_cap = Column(Float)  # 总市值
    created_at = Column(DateTime, default=datetime.now)
    
    stock = relationship("Stock")

class Portfolio(Base):
    """持仓表"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Integer, nullable=False)  # 持股数量
    cost_price = Column(Float, nullable=False)  # 成本价
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("User")
    stock = relationship("Stock")

class Watchlist(Base):
    """关注列表"""
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
    stock = relationship("Stock")

class AlertRule(Base):
    """提醒规则表"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)  # 规则名称
    rule_type = Column(String(50), nullable=False)  # 规则类型：price/pe/change/portfolio
    condition = Column(JSON, nullable=False)  # 触发条件，JSON格式
    notify_type = Column(String(50), default="feishu")  # 通知方式：feishu/email
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("User")

class AnalysisReport(Base):
    """分析报告表"""
    __tablename__ = "analysis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    report_type = Column(String(50), nullable=False)  # 报告类型：stock/portfolio/quant
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # 报告内容
    score = Column(Float)  # 综合评分
    suggestion = Column(String(50))  # 建议：买入/持有/卖出
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
    stock = relationship("Stock")

class QuantStrategy(Base):
    """量化策略表"""
    __tablename__ = "quant_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategy_code = Column(String(50), unique=True, nullable=False)  # 策略编码
    parameters = Column(JSON)  # 策略参数
    is_builtin = Column(Boolean, default=True)  # 是否内置策略
    created_at = Column(DateTime, default=datetime.now)

class BacktestRecord(Base):
    """回测记录表"""
    __tablename__ = "backtest_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("quant_strategies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=False)
    parameters = Column(JSON)  # 回测参数
    result = Column(JSON)  # 回测结果
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
    strategy = relationship("QuantStrategy")

class PortfolioIncomeRecord(Base):
    """持仓收益记录表"""
    __tablename__ = "portfolio_income_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_date = Column(String(20), nullable=False, index=True)  # 记录日期
    total_value = Column(Float, nullable=False)  # 总市值
    total_profit = Column(Float, nullable=False)  # 总收益
    total_profit_rate = Column(Float, nullable=False)  # 总收益率
    daily_profit = Column(Float, nullable=False)  # 当日收益
    daily_profit_rate = Column(Float, nullable=False)  # 当日收益率
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")

class Notification(Base):
    """通知记录表"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    notify_type = Column(String(50), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
