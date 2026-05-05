
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.app.services.stock import sync_stock_list, sync_stock_daily_data
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

def init_scheduler():
    """初始化定时任务"""
    # 每日17点同步所有股票日线数据（收盘后）
    scheduler.add_job(
        sync_stock_list,
        trigger=CronTrigger(hour=17, minute=0, second=0),
        id="sync_stock_list",
        name="每日同步股票列表",
        replace_existing=True
    )
    # 每日17点30分同步所有股票日线数据（收盘后）
    # 这里可以根据需要调整，比如只同步关注的股票，减少请求量
    scheduler.add_job(
        sync_all_stock_daily_data,
        trigger=CronTrigger(hour=17, minute=30, second=0),
        id="sync_all_stock_daily_data",
        name="每日同步股票日线数据",
        replace_existing=True
    )
    # 启动调度器
    scheduler.start()
    print("✅ 定时任务调度器启动成功")

def sync_all_stock_daily_data():
    """同步所有股票的日线数据（实际使用时建议只同步关注的股票，避免请求过多）"""
    from backend.app.core.database import SessionLocal
    from backend.app.models import Stock
    db = SessionLocal()
    try:
        stocks = db.query(Stock.code).all()
        for stock in stocks:
            sync_stock_daily_data(stock.code)
        print(f"✅ 成功同步{len(stocks)}只股票的日线数据")
    except Exception as e:
        print(f"❌ 同步日线数据失败: {str(e)}")
    finally:
        db.close()

def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        print("✅ 定时任务调度器已关闭")
