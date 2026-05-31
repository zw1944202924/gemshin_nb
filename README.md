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
2. 执行 `docker compose up -d` 启动 MySQL `8.4` 和 Redis `7.2`
3. 在 `apps/api` 中创建虚拟环境并安装依赖
4. 执行 Django 迁移并启动 API
5. 在 `apps/web` 中安装依赖并启动前端

如果本地 `mysql_data` 卷是用其他 MySQL 主版本初始化的，切换版本前先重建该卷；当前仓库默认使用 MySQL `8.4`，不要在保留 `8.4` 数据目录的情况下回退到 `8.0`。
如果本地卷是早先带 `mysql_native_password` 启动参数的版本初始化出来的，也要先重建该卷；否则旧账号认证插件元数据会保留在数据目录里，Django 连接时会报 `Plugin 'mysql_native_password' is not loaded`。
`.env` 中的 `MYSQL_PORT` 同时决定 Docker 在宿主机暴露的 MySQL 端口，以及 Django 连接 MySQL 时使用的端口；如果改这个值，compose 和应用会一起跟随。
如果前端运行在 `localhost:3000` 或 `3001`，后端需要允许对应浏览器来源；默认 `.env.example` 已经把常见本地来源写进 `CORS_ALLOWED_ORIGINS`。

后端最小可复现命令：

```bash
cp .env.example .env
docker compose up -d

cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
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

## 最小认证闭环

当前仓库已经提供第一条真实认证链路，默认约定如下：

- 后端认证接口：
  - `POST /api/v1/auth/login/`
  - `GET /api/v1/auth/me/`
  - `POST /api/v1/auth/logout/`
  - `GET /api/v1/protected/`
- 前端页面：
  - `/login` 登录页
  - `/dashboard` 受保护页面，未登录时自动跳转到 `/login`
- 登录态机制：
  - 后端登录成功后生成随机 Bearer token，并把服务端登录态写入缓存
  - 前端用 `gemshin_token` cookie 持有 token，并在访问受保护接口时自动附带 `Authorization: Bearer <token>`
  - token 默认有效期 `8` 小时，可通过 `AUTH_TOKEN_MAX_AGE_SECONDS` 调整
  - 调用 `POST /api/v1/auth/logout/` 会删除当前 token 对应的服务端登录态，已退出 token 不能继续访问受保护接口

本地联调建议：

1. 在 `apps/api` 执行 `python manage.py createsuperuser`，创建一个可登录账号
2. 启动 Django API 与 Nuxt 前端
3. 访问 `http://127.0.0.1:3000/login`
4. 使用刚创建的账号登录，确认会跳转到 `/dashboard`
5. 打开新标签直接访问 `/dashboard`，确认未退出前仍可访问
6. 点击“退出登录”后再次访问 `/dashboard`，确认会被拦回 `/login`

后端认证链路的最小自测命令：

```bash
cd apps/api
./.venv/bin/python manage.py test apps.core --settings=config.settings.test
```

## 第一阶段目标

- 跑通新的前后端骨架
- 明确 `/api/v1/...` 接口约定
- 建立认证闭环
- 选一个最小示例业务模块继续实现

## 说明

- 旧资产已单独做本地压缩备份，不再保留在当前 Git 工作树中
- 旧设计文档不再作为当前仓库的主线内容，后续仅按新底座方向补文档
- `apps/web` 的运行与扩展说明见 `apps/web/README.md`
