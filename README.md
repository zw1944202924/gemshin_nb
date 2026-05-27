# gemshin_nb

面向长期扩展、便于人和 agent 协同开发的产品底座仓库。旧版实现与旧设计稿已经从工作树移除，并在本地完成压缩备份；当前仓库内容以新的 monorepo 骨架为准。

## 当前方向

- 前端：Nuxt，后续接入 `nuxt-ui-templates/dashboard` 与 `nuxt/ui`
- 后端：Django + Django REST Framework
- 基础设施：MySQL + Redis
- 仓库形态：monorepo

## 当前目录

```text
apps/
  web/            # Nuxt 起步工程
  api/            # Django 起步工程
packages/
  shared-types/   # 共享约定占位
  eslint-config/  # 前端共享配置占位
infra/
  docker/
  scripts/
docs/
  architecture/
  api/
  onboarding/
```

## 本地启动

1. 复制 `.env.example` 为 `.env`
2. 执行 `docker compose up -d` 启动 MySQL `8.4` 和 Redis `7.2`
3. 在 `apps/api` 中创建虚拟环境并安装依赖
4. 执行 Django 迁移并启动 API
5. 在 `apps/web` 中安装依赖并启动前端

如果本地 `mysql_data` 卷是用其他 MySQL 主版本初始化的，切换版本前先重建该卷；当前仓库默认使用 MySQL `8.4`，不要在保留 `8.4` 数据目录的情况下回退到 `8.0`。

后端最小可复现命令：

```bash
cp .env.example .env
docker compose up -d

cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

健康检查会真实访问 MySQL 和 Redis：

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

预期返回：

```json
{"status":"ok","service":"api","checks":{"mysql":"ok","redis":"ok"}}
```

前端启动命令：

```bash
cd apps/web
pnpm install
pnpm dev
```

## 第一阶段目标

- 跑通新的前后端骨架
- 明确 `/api/v1/...` 接口约定
- 建立认证闭环
- 选一个最小示例业务模块继续实现

## 说明

- 旧资产已单独做本地压缩备份，不再保留在当前 Git 工作树中
- 旧设计文档不再作为当前仓库的主线内容，后续仅按新底座方向补文档
