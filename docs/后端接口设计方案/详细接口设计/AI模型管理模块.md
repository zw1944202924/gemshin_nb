# AI模型管理模块接口设计

## 1. 接口列表

| 接口路径 | 方法 | 功能描述 | 请求参数 | 响应数据 | 权限要求 |
|---------|------|---------|---------|---------|----------|
| `/api/v1/ai/model` | GET | 获取AI模型列表 | 无 | `[{"id": int, "name": str, "type": str, "status": str, "version": str, "last_updated": str}]` | 管理员 |
| `/api/v1/ai/model/{id}` | GET | 获取模型详情 | id: int (路径参数，必填) | `{"id": int, "name": str, "type": str, "status": str, "version": str, "config": {}, "performance": {}}` | 管理员 |
| `/api/v1/ai/model/{id}/status` | PUT | 更新模型状态 | id: int (路径参数，必填)<br>status: str (必填，"active"/"inactive") | `{"message": "模型状态更新成功"}` | 管理员 |
| `/api/v1/ai/model/{id}/config` | PUT | 更新模型配置 | id: int (路径参数，必填)<br>config: object (必填，符合模型配置格式) | `{"message": "模型配置更新成功"}` | 管理员 |
| `/api/v1/ai/performance` | GET | 获取模型性能统计 | model_id: int (可选) | `{"models": [{"id": int, "name": str, "accuracy": float, "precision": float, "recall": float, "f1_score": float, "last_evaluated": str}]}` | 管理员 |

## 2. 接口详情

### 2.1 获取AI模型列表

**接口路径**：`/api/v1/ai/model`
**方法**：GET
**功能描述**：获取AI模型列表
**请求参数**：无
**响应数据**：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "StockAnalysisCrew",
      "type": "stock_analysis",
      "status": "active",
      "version": "1.0.0",
      "last_updated": "2026-01-01 10:00:00"
    },
    {
      "id": 2,
      "name": "PortfolioAnalysisCrew",
      "type": "portfolio_analysis",
      "status": "active",
      "version": "1.0.0",
      "last_updated": "2026-01-01 10:00:00"
    },
    {
      "id": 3,
      "name": "WatchlistAnalysisCrew",
      "type": "watchlist_analysis",
      "status": "active",
      "version": "1.0.0",
      "last_updated": "2026-01-01 10:00:00"
    }
  ]
}
```

### 2.2 获取模型详情

**接口路径**：`/api/v1/ai/model/{id}`
**方法**：GET
**功能描述**：获取模型详情
**请求参数**：
- id: int (路径参数，必填)

**响应数据**：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "StockAnalysisCrew",
    "type": "stock_analysis",
    "status": "active",
    "version": "1.0.0",
    "config": {
      "agents": [
        "chief_analyst",
        "industry_researcher",
        "financial_analyst",
        "technical_analyst",
        "sentiment_analyst"
      ],
      "timeout": 300,
      "max_iterations": 5
    },
    "performance": {
      "accuracy": 0.85,
      "precision": 0.82,
      "recall": 0.88,
      "f1_score": 0.85,
      "last_evaluated": "2026-01-01 10:00:00"
    }
  }
}
```

### 2.3 更新模型状态

**接口路径**：`/api/v1/ai/model/{id}/status`
**方法**：PUT
**功能描述**：更新模型状态
**请求参数**：
- id: int (路径参数，必填)
- status: str (必填，"active"/"inactive")

**响应数据**：
```json
{
  "code": 200,
  "message": "模型状态更新成功",
  "data": {}
}
```

### 2.4 更新模型配置

**接口路径**：`/api/v1/ai/model/{id}/config`
**方法**：PUT
**功能描述**：更新模型配置
**请求参数**：
- id: int (路径参数，必填)
- config: object (必填，符合模型配置格式)

**响应数据**：
```json
{
  "code": 200,
  "message": "模型配置更新成功",
  "data": {}
}
```

### 2.5 获取模型性能统计

**接口路径**：`/api/v1/ai/performance`
**方法**：GET
**功能描述**：获取模型性能统计
**请求参数**：
- model_id: int (可选)

**响应数据**：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "models": [
      {
        "id": 1,
        "name": "StockAnalysisCrew",
        "accuracy": 0.85,
        "precision": 0.82,
        "recall": 0.88,
        "f1_score": 0.85,
        "last_evaluated": "2026-01-01 10:00:00"
      },
      {
        "id": 2,
        "name": "PortfolioAnalysisCrew",
        "accuracy": 0.88,
        "precision": 0.85,
        "recall": 0.90,
        "f1_score": 0.87,
        "last_evaluated": "2026-01-01 10:00:00"
      },
      {
        "id": 3,
        "name": "WatchlistAnalysisCrew",
        "accuracy": 0.90,
        "precision": 0.88,
        "recall": 0.92,
        "f1_score": 0.90,
        "last_evaluated": "2026-01-01 10:00:00"
      }
    ]
  }
}
```