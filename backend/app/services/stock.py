
import akshare as ak
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models import Stock, StockDailyData
from backend.app.core.database import SessionLocal

def get_all_a_stock_list():
    """获取所有A股股票列表"""
    try:
        # 获取沪市A股
        sh_df = ak.stock_info_sh_name_code(symbol="主板A股")
        sh_df["market"] = "SH"
        sh_df = sh_df.rename(columns={"证券代码": "code", "证券简称": "name", "上市日期": "listing_date"})
        # 获取深市A股
        sz_df = ak.stock_info_sz_name_code(symbol="A股列表")
        sz_df["market"] = "SZ"
        sz_df = sz_df.rename(columns={"A股代码": "code", "A股简称": "name", "上市日期": "listing_date"})
        # 获取北交所股票
        bj_df = ak.stock_info_bj_name_code()
        bj_df["market"] = "BJ"
        bj_df = bj_df.rename(columns={"证券代码": "code", "证券简称": "name", "上市日期": "listing_date"})
        # 合并数据
        df = pd.concat([sh_df[["code", "name", "market", "listing_date"]], 
                       sz_df[["code", "name", "market", "listing_date"]], 
                       bj_df[["code", "name", "market", "listing_date"]]], ignore_index=True)
        # 去重
        df = df.drop_duplicates(subset=["code"], keep="first")
        return df.to_dict("records")
    except Exception as e:
        print(f"获取股票列表失败: {str(e)}")
        return []

def get_stock_daily_data(stock_code: str, start_date: str = None, end_date: str = None):
    """获取股票日线数据"""
    try:
        # 默认获取最近一年的数据
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now().replace(year=datetime.now().year-1)).strftime("%Y%m%d")
        # 调用AkShare接口
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="hfq")
        if df.empty:
            return []
        # 重命名列
        df = df.rename(columns={
            "日期": "trade_date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "turnover",
            "市盈率": "pe",
            "市净率": "pb",
            "总市值": "total_market_cap"
        })
        # 转换日期格式
        df["trade_date"] = df["trade_date"].astype(str).str.replace("-", "")
        return df.to_dict("records")
    except Exception as e:
        print(f"获取股票{stock_code}日线数据失败: {str(e)}")
        return []

def sync_stock_list(db: Session = None):
    """同步股票列表到数据库"""
    if not db:
        db = SessionLocal()
    try:
        stock_list = get_all_a_stock_list()
        if not stock_list:
            return False, "获取股票列表失败"
        # 批量插入或更新
        for stock in stock_list:
            db_stock = db.query(Stock).filter(Stock.code == stock["code"]).first()
            if not db_stock:
                db_stock = Stock(**stock)
                db.add(db_stock)
            else:
                db_stock.name = stock["name"]
                db_stock.market = stock["market"]
                db_stock.listing_date = stock["listing_date"]
        db.commit()
        return True, f"成功同步{len(stock_list)}只股票"
    except Exception as e:
        db.rollback()
        return False, f"同步股票列表失败: {str(e)}"
    finally:
        db.close()

def sync_stock_daily_data(stock_code: str, start_date: str = None, end_date: str = None, db: Session = None):
    """同步股票日线数据到数据库"""
    if not db:
        db = SessionLocal()
    try:
        # 先获取股票ID
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            return False, f"股票{stock_code}不存在"
        # 获取日线数据
        daily_data = get_stock_daily_data(stock_code, start_date, end_date)
        if not daily_data:
            return False, f"获取股票{stock_code}日线数据失败"
        # 批量插入或更新
        count = 0
        for data in daily_data:
            db_data = db.query(StockDailyData).filter(
                StockDailyData.stock_id == stock.id,
                StockDailyData.trade_date == data["trade_date"]
            ).first()
            if not db_data:
                data["stock_id"] = stock.id
                db.add(StockDailyData(**data))
                count += 1
            else:
                # 更新数据
                for key, value in data.items():
                    setattr(db_data, key, value)
        db.commit()
        return True, f"成功同步{count}条{stock_code}日线数据"
    except Exception as e:
        db.rollback()
        return False, f"同步股票{stock_code}日线数据失败: {str(e)}"
    finally:
        db.close()
