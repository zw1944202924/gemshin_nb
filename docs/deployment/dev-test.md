# 测试环境部署准备

## 目标

在同一台阿里云服务器上准备一套与生产隔离的 `gemshin_nb` 测试环境，用于验证 `dev` 分支、数据库迁移、账号权限、OIDC 和 new_api 接入。

当前服务器上的测试环境已经迁移到 `/home/admin` 下统一管理，并且 `gemshin_nb` 测试项目与 `new_api` 测试项目拆分为两套独立 compose。

## 已确认配置

- Gemshin 测试域名：`dev.991hahahanxsm.xyz`
- Gemshin 测试标准目录：`/home/admin/gemshin_nb-test/app`
- newapi-test 标准目录：`/home/admin/new_api-test`
- Gemshin 测试 Compose 项目：`gemshin-nb-test`
- newapi-test Compose 项目：`new-api-test`
- Gemshin Web 宿主机端口：`127.0.0.1:3101`
- Gemshin API 宿主机端口：`127.0.0.1:8101`
- newapi-test 宿主机端口：`127.0.0.1:3002`
- newapi-test 访问范围：仅服务器本机或 SSH 隧道访问，不配置公网 DNS，不通过 Nginx 暴露
- new_api 镜像固定为生产当前 digest：`calciumion/new-api@sha256:5a4ca9705f13a000ea85a43c179c4f4f6c6409cdee5b2d7a56df32a9818c783a`

`dev.991hahahanxsm.xyz` 已解析到服务器 `218.244.151.41`。newapi-test 不允许暴露到公网，因此不需要也不应配置 `newapi-dev` 之类的公网 DNS。

## 隔离边界

测试环境使用独立的 Docker Compose 项目、容器、网络、数据卷、端口和挂载目录：

| 类型 | 生产 | 测试 |
| --- | --- | --- |
| 代码目录 | `/home/admin/gemshin_nb-prod` | `/home/admin/gemshin_nb-test/app` |
| Compose 项目 | `gemshin_nb` | `gemshin-nb-test` |
| Web | `gemshin_nb-web-1` / `127.0.0.1:3100` | `gemshin-nb-test-web` / `127.0.0.1:3101` |
| API | `gemshin_nb-api-1` / `127.0.0.1:8100` | `gemshin-nb-test-api` / `127.0.0.1:8101` |
| MySQL | `gemshin_nb-mysql-1` | `gemshin-nb-test-db` |
| Redis | `gemshin_nb-redis-1` | `gemshin-nb-test-redis` |
| new_api | `new-api` / `127.0.0.1:3000` | `new-api-test` / `127.0.0.1:3002`，不暴露公网 |
| new_api 数据 | 生产现有目录 | `/home/admin/new_api-test/data` |
| new_api 日志 | 生产现有目录 | `/home/admin/new_api-test/logs` |

禁止复用生产数据库、Redis、数据卷、OIDC 私钥、new_api 生产实例、生产客户端密钥和生产业务数据。

## Gemshin 测试环境首次准备

在服务器标准目录拉取要验证的明确提交 SHA 后，复制测试环境变量模板：

```bash
mkdir -p /home/admin/gemshin_nb-test
cd /home/admin/gemshin_nb-test
git clone <repo-url> app
cd /home/admin/gemshin_nb-test/app
cp .env.dev.example .env.dev
```

必须替换：

- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `DJANGO_SECRET_KEY`
- `OIDC_RSA_PRIVATE_KEY`
- `ADMIN_PASSWORD`

生成测试专用 OIDC 私钥示例：

```bash
openssl genrsa 2048 | awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}'
```

不要复制生产私钥、生产数据库密码、生产 new_api 密钥或生产 Token。

## 启动 Gemshin 测试环境

```bash
cd /home/admin/gemshin_nb-test/app
chmod +x infra/scripts/deploy-dev.sh
./infra/scripts/deploy-dev.sh
```

脚本会执行：

- 确认测试 MySQL/Redis volume 存在，缺失时自动创建
- 构建 `gemshin-nb-test-api` 和 `gemshin-nb-test-web`
- 启动 `mysql`、`redis`
- 启动 `api`、`web`
- 执行 `migrate`
- 执行 `seed_modules`
- 执行 `seed_roles`
- 检查 `http://127.0.0.1:8101/api/v1/health/`

## 按最新版重新部署测试环境

服务器测试目录已经存在时，推荐使用重部署脚本从远端拉取最新版 `dev` 并部署：

```bash
cd /home/admin/gemshin_nb-test/app
chmod +x infra/scripts/redeploy-dev-latest.sh
./infra/scripts/redeploy-dev-latest.sh
```

脚本默认会：

- 检查当前目录是否为 Git 仓库；
- 拒绝覆盖未提交的服务器本地代码改动；
- 拉取 `origin` 最新内容；
- 切换到 `origin/dev` 最新提交；
- 执行 `infra/scripts/deploy-dev.sh`；
- 检查 `https://dev.991hahahanxsm.xyz/api/v1/health/`。

如果确认服务器代码目录里的本地改动可以丢弃，可强制按最新版覆盖：

```bash
cd /home/admin/gemshin_nb-test/app
./infra/scripts/redeploy-dev-latest.sh --force
```

如需同时刷新并重启 `newapi-test` 的 compose 文件：

```bash
cd /home/admin/gemshin_nb-test/app
./infra/scripts/redeploy-dev-latest.sh --with-newapi
```

可指定其他分支、标签或提交：

```bash
cd /home/admin/gemshin_nb-test/app
./infra/scripts/redeploy-dev-latest.sh --ref dev
```

## 启动 newapi-test

`newapi-test` 已从 Gemshin 测试 compose 中拆出，单独放在 `/home/admin/new_api-test` 管理。容器只监听 `127.0.0.1:3002`，公网入口必须走 Gemshin 测试域名下的受保护子路径 `/assistant/new-api/`。

首次准备：

```bash
mkdir -p /home/admin/new_api-test
cp /home/admin/gemshin_nb-test/app/infra/new_api-test/docker-compose.yml /home/admin/new_api-test/docker-compose.yml
cd /home/admin/new_api-test
mkdir -p data logs
cat > .env <<'EOF'
NEWAPI_FRONTEND_BASE_URL=https://dev.991hahahanxsm.xyz/assistant/new-api
NEWAPI_SESSION_SECRET=<测试环境随机值>
NEWAPI_CRYPTO_SECRET=<测试环境随机值>
EOF
```

`NEWAPI_SESSION_SECRET` 和 `NEWAPI_CRYPTO_SECRET` 必须使用测试环境独立随机值，不得复用生产 new_api 或生产 Gemshin 的任何密钥。

启动或更新：

```bash
cd /home/admin/new_api-test
/home/admin/gemshin_nb-test/app/infra/scripts/deploy-newapi-test.sh
```

如果脚本不在当前目录，也可以直接执行：

```bash
docker compose --project-name new-api-test -f docker-compose.yml up -d
curl -fsS http://127.0.0.1:3002/api/status
```

## Nginx

安装测试 Nginx 配置：

```bash
cp infra/nginx/gemshin_nb_dev.conf /etc/nginx/conf.d/gemshin_nb_dev.conf
nginx -t
systemctl reload nginx
```

HTTPS 证书建议分别覆盖：

- `dev.991hahahanxsm.xyz`

签发证书前先确认不会覆盖现有 `multica.991hahahanxsm.xyz` 和生产域名证书配置。

## OIDC 与 newapi-test 联调

Gemshin 测试环境作为 OIDC issuer：

```text
https://dev.991hahahanxsm.xyz/api/v1/oidc
```

newapi-test 作为 OIDC 客户端，部署后在 new_api 管理后台配置。当前固定镜像为：

```text
calciumion/new-api@sha256:5a4ca9705f13a000ea85a43c179c4f4f6c6409cdee5b2d7a56df32a9818c783a
```

该版本的基础环境变量能力包含 `FRONTEND_BASE_URL`、`SESSION_SECRET`、`CRYPTO_SECRET`，并支持 OIDC 登录方式。因为 newapi-test 不暴露公网，管理后台访问与首次 OIDC 配置建议先通过 SSH 隧道完成：

```bash
ssh -L 3002:127.0.0.1:3002 root@218.244.151.41
```

打开本机浏览器访问：

```text
http://127.0.0.1:3002
```

OIDC 配置：

- Discovery：`https://dev.991hahahanxsm.xyz/api/v1/oidc/.well-known/openid-configuration`
- Redirect URI：正式内嵌联调使用 `https://dev.991hahahanxsm.xyz/assistant/new-api/` 下 new_api 实际 OIDC 回调路径；SSH 隧道只用于首次进入后台配置
- Post logout redirect URI：登记 `https://dev.991hahahanxsm.xyz/assistant`
- 授权模式：Authorization Code + PKCE S256
- Scope：`openid profile email`
- 用户绑定键：必须使用 Gemshin 下发的 `sub`，不要用可变用户名做运行时绑定
- 登录入口：关闭或隐藏 new_api 本地账号密码注册/登录，仅保留 OIDC；如当前版本后台无法完全关闭本地入口，必须至少依靠 Nginx `auth_request` 保证外部未登录 Gemshin 的访问先被拒绝

测试环境客户端 ID、客户端密钥、用户映射、额度和渠道都必须单独创建，不能复用生产配置。

Gemshin 侧 Django Admin 创建 `oauth2_provider.Application` 时：

- `client_type`：public
- `authorization_grant_type`：authorization-code
- `algorithm`：RS256
- `skip_authorization`：测试阶段建议开启
- `redirect_uris` 和 `post_logout_redirect_uris` 必须逐条填写，不允许通配符

内嵌入口：

- 用户先登录 `https://dev.991hahahanxsm.xyz/`
- 进入 Gemshin 页面 `/assistant`
- 页面内嵌 iframe 指向 `/assistant/new-api/`
- Nginx 对 `/assistant/new-api/` 执行 `auth_request /api/v1/assistant/new-api/auth/`
- auth 端点只接受当前 Gemshin 登录态 Cookie 或 Bearer token；未登录、已停用、改密/停用后已失效、首次登录未完成改密的用户会被拒绝
- Nginx 只把通过鉴权的请求反代到 `127.0.0.1:3002`，并重写 Cookie Path、Redirect、静态资源前缀，保留 WebSocket/流式连接升级头

## 验证清单

```bash
cd /home/admin/gemshin_nb-test/app
docker compose --project-name gemshin-nb-test --env-file .env.dev -f docker-compose.dev.yml ps
curl -fsS http://127.0.0.1:8101/api/v1/health/
curl -fsS https://dev.991hahahanxsm.xyz/api/v1/health/

cd /home/admin/new_api-test
docker compose --project-name new-api-test -f docker-compose.yml ps
curl -fsS http://127.0.0.1:3002/api/status
```

OIDC 验证：

- Discovery 可访问
- JWKS 可访问
- Authorization Code + PKCE 可完成
- `state` / `nonce` 校验正常
- Token 和 UserInfo 正常
- 已登录 Gemshin 测试环境后进入 `/assistant` 内嵌的 newapi-test，不需要二次输入密码
- 退出、停用账号、改密后 Token 和会话按预期失效
- 未登录浏览器访问 `https://dev.991hahahanxsm.xyz/assistant/new-api/` 会跳回 Gemshin 登录入口
- 停用用户或已强制改密用户访问 `/assistant/new-api/` 返回拒绝，不会触达 newapi-test

隔离验证：

- `docker volume ls` 中测试卷与生产卷不同
- `docker network ls` 中测试网络与生产网络不同
- 测试 MySQL 库名为 `gemshin_dev`
- newapi-test 数据目录为 `/home/admin/new_api-test/data`
- 不读取或写入生产 new_api 数据目录
- 两个 Gemshin 测试账号首次进入 new_api 后，在 new_api 用户、额度、令牌、调用日志维度互不可见、互不可操作
- 通过 `curl -I http://127.0.0.1:3002` 只能在服务器本机或 SSH 隧道访问；外网不得存在独立 new_api 域名、端口或 Nginx server
- Nginx 只有测试配置 `infra/nginx/gemshin_nb_dev.conf` 包含 `/assistant/new-api/`，生产配置不得同步该 location，除非另行授权

## 停止与回滚

停止 Gemshin 测试环境：

```bash
cd /home/admin/gemshin_nb-test/app
docker compose --project-name gemshin-nb-test --env-file .env.dev -f docker-compose.dev.yml down
```

停止 newapi-test：

```bash
cd /home/admin/new_api-test
docker compose --project-name new-api-test -f docker-compose.yml down
```

保留测试数据时不要删除 Gemshin 测试 volume 和 `/home/admin/new_api-test/data`。

回滚内嵌入口时：

1. 从 `/etc/nginx/conf.d/gemshin_nb_dev.conf` 移除 `/assistant/new-api/`、`@gemshin_login`、`@gemshin_forbidden` 以及顶部 `map $http_upgrade` 配置，或恢复到上一版测试 Nginx 配置；
2. 执行 `nginx -t && systemctl reload nginx`；
3. 如需停止 newapi-test，执行 `docker compose --project-name new-api-test -f /home/admin/new_api-test/docker-compose.yml down`；
4. 保留 Gemshin OIDC 配置不会影响普通 Gemshin 登录；如需彻底回滚，再在 Django Admin 中停用对应测试 OIDC Application。

如需完全清理测试环境：

```bash
cd /home/admin/gemshin_nb-test/app
docker compose --project-name gemshin-nb-test --env-file .env.dev -f docker-compose.dev.yml down -v

cd /home/admin/new_api-test
docker compose --project-name new-api-test -f docker-compose.yml down
rm -rf /home/admin/new_api-test/data /home/admin/new_api-test/logs

rm -f /etc/nginx/conf.d/gemshin_nb_dev.conf
nginx -t
systemctl reload nginx
```

清理前必须再次确认目标是测试环境，不能删除生产容器、生产卷或生产 new_api 数据目录。

旧目录 `/opt/gemshin-dev/app` 只作为历史回滚目录保留，不再作为标准测试部署目录。
