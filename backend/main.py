
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.database import engine, Base
from backend.app.core.scheduler import init_scheduler, shutdown_scheduler
from backend.app.api import stock, user, portfolio, watchlist, alert, analysis, quant, backtest, notification

# 创建所有数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI股票分析助手", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user.router, prefix="/api/user", tags=["用户管理"])
app.include_router(stock.router, prefix="/api/stock", tags=["股票数据"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["持仓管理"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["关注列表"])
app.include_router(alert.router, prefix="/api/alert", tags=["提醒规则"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["AI分析"])
app.include_router(quant.router, prefix="/api/quant", tags=["量化选股"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["回测"])
app.include_router(notification.router, prefix="/api/notification", tags=["通知管理"])

# 启动定时任务
@app.on_event("startup")
def startup_event():
    init_scheduler()

# 关闭定时任务
@app.on_event("shutdown")
def shutdown_event():
    shutdown_scheduler()

# 健康检查接口
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "AI股票分析助手服务运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
