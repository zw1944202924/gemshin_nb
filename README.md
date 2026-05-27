# gemshin_nb

面向长期扩展、便于人和 agent 协同开发的产品底座仓库。旧版实现与旧设计稿已经从工作树移除，并在本地完成压缩备份；当前仓库内容以新的 monorepo 骨架为准。

## 当前方向

- 前端：Nuxt，`apps/web` 已接入 `@nuxt/ui` 并建立 dashboard 基线，默认按离线友好的本地字体栈启动
- 后端：Django + Django REST Framework
- 基础设施：MySQL + Redis
- 仓库形态：monorepo

## 当前目录

```text
apps/
  web/            # Nuxt + @nuxt/ui dashboard 基线
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
2. 执行 `docker compose up -d` 启动 MySQL 和 Redis
3. 在 `apps/api` 中创建虚拟环境并安装依赖：`pip install -r requirements.txt`
4. 在 `apps/web` 中安装依赖：`npm install`
5. 分别启动：
   - API：`python manage.py runserver 0.0.0.0:8000`
   - Web：`npm run dev`

## 第一阶段目标

- 跑通新的前后端骨架
- 明确 `/api/v1/...` 接口约定
- 建立认证闭环
- 选一个最小示例业务模块继续实现

## 说明

- 旧资产已单独做本地压缩备份，不再保留在当前 Git 工作树中
- 旧设计文档不再作为当前仓库的主线内容，后续仅按新底座方向补文档
- `apps/web` 的运行与扩展说明见 `apps/web/README.md`
