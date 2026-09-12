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

`newapi-test` 已从 Gemshin 测试 compose 中拆出，单独放在 `/home/admin/new_api-test` 管理。

首次准备：

```bash
mkdir -p /home/admin/new_api-test
cp /home/admin/gemshin_nb-test/app/infra/new_api-test/docker-compose.yml /home/admin/new_api-test/docker-compose.yml
cd /home/admin/new_api-test
mkdir -p data logs
```

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

newapi-test 作为 OIDC 客户端，部署后在 new_api 管理后台配置。因为 newapi-test 不暴露公网，管理后台访问与浏览器联调建议通过 SSH 隧道完成：

```bash
ssh -L 3002:127.0.0.1:3002 root@218.244.151.41
```

打开本机浏览器访问：

```text
http://127.0.0.1:3002
```

OIDC 配置：

- Discovery：`https://dev.991hahahanxsm.xyz/api/v1/oidc/.well-known/openid-configuration`
- Redirect URI：以 SSH 隧道访问地址对应的 newapi-test 实际回调地址为准，例如 `http://127.0.0.1:3002/<newapi-callback-path>`
- 授权模式：Authorization Code + PKCE S256
- Scope：`openid profile email`

测试环境客户端 ID、客户端密钥、用户映射、额度和渠道都必须单独创建，不能复用生产配置。

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
- 已登录 Gemshin 测试环境后进入 `newapi-test` 不需要二次输入密码
- 退出、停用账号、改密后 Token 和会话按预期失效

隔离验证：

- `docker volume ls` 中测试卷与生产卷不同
- `docker network ls` 中测试网络与生产网络不同
- 测试 MySQL 库名为 `gemshin_dev`
- newapi-test 数据目录为 `/home/admin/new_api-test/data`
- 不读取或写入生产 new_api 数据目录

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
