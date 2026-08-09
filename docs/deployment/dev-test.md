# 测试环境部署准备

## 目标

在同一台阿里云服务器上准备一套与生产隔离的 `gemshin_nb` 测试环境，用于验证 `dev` 分支、数据库迁移、账号权限、OIDC 和 new_api 接入。

本阶段只补齐仓库内配置、脚本和文档。真实服务器部署、证书签发、new_api 测试实例初始化和 OIDC 客户端创建，另行执行。

## 已确认配置

- Gemshin 测试域名：`dev.991hahahanxsm.xyz`
- Gemshin Web 宿主机端口：`127.0.0.1:3101`
- Gemshin API 宿主机端口：`127.0.0.1:8101`
- newapi-test 宿主机端口：`127.0.0.1:3002`
- newapi-test 推荐域名：`newapi-dev.991hahahanxsm.xyz`
- new_api 镜像固定为生产当前 digest：`calciumion/new-api@sha256:5a4ca9705f13a000ea85a43c179c4f4f6c6409cdee5b2d7a56df32a9818c783a`

`dev.991hahahanxsm.xyz` 已解析到服务器 `218.244.151.41`。`newapi-dev.991hahahanxsm.xyz` 需要在真实部署前补 DNS 解析，或改为用户确认的其他测试域名。

## 隔离边界

测试环境使用独立的 Docker Compose 项目、容器、网络、数据卷、端口和挂载目录：

| 类型 | 生产 | 测试 |
| --- | --- | --- |
| Compose 项目 | `gemshin_nb` | `gemshin-dev` |
| Web | `gemshin_nb-web-1` / `127.0.0.1:3100` | `gemshin-dev-web` / `127.0.0.1:3101` |
| API | `gemshin_nb-api-1` / `127.0.0.1:8100` | `gemshin-dev-api` / `127.0.0.1:8101` |
| MySQL | `gemshin_nb-mysql-1` | `gemshin-dev-db-test` |
| Redis | `gemshin_nb-redis-1` | `gemshin-dev-redis-test` |
| new_api | `new-api` / `127.0.0.1:3000` | `gemshin-dev-newapi-test` / `127.0.0.1:3002` |
| new_api 数据 | `/home/admin/new-api/data` | `/opt/gemshin-dev/new-api/data` |
| new_api 日志 | `/home/admin/new-api/logs` | `/opt/gemshin-dev/new-api/logs` |

禁止复用生产数据库、Redis、数据卷、OIDC 私钥、new_api 生产实例、生产客户端密钥和生产业务数据。

## 首次准备

在服务器拉取要验证的明确提交 SHA 后，复制测试环境变量模板：

```bash
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

## 启动测试环境

```bash
chmod +x infra/scripts/deploy-dev.sh
./infra/scripts/deploy-dev.sh
```

脚本会执行：

- 构建 `gemshin-dev-api` 和 `gemshin-dev-web`
- 启动 `mysql`、`redis`、`newapi`
- 启动 `api`、`web`
- 执行 `migrate`
- 执行 `seed_modules`
- 执行 `seed_roles`
- 检查 `http://127.0.0.1:8101/api/v1/health/`

## Nginx

安装测试 Nginx 配置：

```bash
cp infra/nginx/gemshin_nb_dev.conf /etc/nginx/conf.d/gemshin_nb_dev.conf
nginx -t
systemctl reload nginx
```

HTTPS 证书建议分别覆盖：

- `dev.991hahahanxsm.xyz`
- `newapi-dev.991hahahanxsm.xyz`

签发证书前先确认不会覆盖现有 `multica.991hahahanxsm.xyz` 和生产域名证书配置。

## OIDC 与 newapi-test 联调

Gemshin 测试环境作为 OIDC issuer：

```text
https://dev.991hahahanxsm.xyz/api/v1/oidc
```

newapi-test 作为 OIDC 客户端，部署后在 new_api 管理后台配置：

- Discovery：`https://dev.991hahahanxsm.xyz/api/v1/oidc/.well-known/openid-configuration`
- Redirect URI：以 `newapi-dev.991hahahanxsm.xyz` 实际回调地址为准
- 授权模式：Authorization Code + PKCE S256
- Scope：`openid profile email`

测试环境客户端 ID、客户端密钥、用户映射、额度和渠道都必须单独创建，不能复用生产配置。

## 验证清单

```bash
docker compose --project-name gemshin-dev --env-file .env.dev -f docker-compose.dev.yml ps
curl -fsS http://127.0.0.1:8101/api/v1/health/
curl -fsS https://dev.991hahahanxsm.xyz/api/v1/health/
```

OIDC 验证：

- Discovery 可访问
- JWKS 可访问
- Authorization Code + PKCE 可完成
- `state` / `nonce` 校验正常
- Token 和 UserInfo 正常
- 已登录 `gemshin-dev` 后进入 `newapi-test` 不需要二次输入密码
- 退出、停用账号、改密后 Token 和会话按预期失效

隔离验证：

- `docker volume ls` 中测试卷与生产卷不同
- `docker network ls` 中测试网络与生产网络不同
- 测试 MySQL 库名为 `gemshin_dev`
- newapi-test 数据目录为 `/opt/gemshin-dev/new-api/data`
- 不读取或写入 `/home/admin/new-api/data`

## 停止与回滚

停止测试环境：

```bash
docker compose --project-name gemshin-dev --env-file .env.dev -f docker-compose.dev.yml down
```

保留测试数据时不要删除 volume 和 `/opt/gemshin-dev/new-api`。

如需完全清理测试环境：

```bash
docker compose --project-name gemshin-dev --env-file .env.dev -f docker-compose.dev.yml down -v
rm -rf /opt/gemshin-dev/new-api
rm -f /etc/nginx/conf.d/gemshin_nb_dev.conf
nginx -t
systemctl reload nginx
```

清理前必须再次确认目标是测试环境，不能删除生产容器、生产卷或生产 new_api 数据目录。
