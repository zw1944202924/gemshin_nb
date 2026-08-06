# 生产部署说明

## 部署目标

- 生产域名：`991hahahanxsm.xyz`
- 不启用 `www` 域名。
- `gemshin_nb` 使用独立 MySQL 和 Redis，不复用 Multica 或 new_api 的数据库服务。
- 应用容器只绑定服务器本机端口，公网入口统一交给服务器 Nginx。

## 服务端口

| 服务 | 宿主机端口 | 说明 |
| --- | --- | --- |
| Web | `127.0.0.1:3100` | Nuxt 生产服务 |
| API | `127.0.0.1:8100` | Django + Gunicorn |
| MySQL | 不暴露宿主机端口 | Docker 网络内部访问 |
| Redis | 不暴露宿主机端口 | Docker 网络内部访问 |

## 首次部署

1. 在服务器拉取 `main` 分支代码。
2. 复制并填写生产环境变量：

```bash
cp .env.production.example .env.production
```

必须替换：

- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `DJANGO_SECRET_KEY`
- `ADMIN_PASSWORD`

产品管理员账号由部署脚本读取 `.env.production` 后自动创建，并分配管理员角色和全部模块权限：

```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=替换为强密码
```

部署脚本每次都会按 `.env.production` 同步该管理员账号的密码和角色权限。需要变更生产管理员密码时，修改 `ADMIN_PASSWORD` 后重新执行部署脚本。

3. 执行部署脚本：

```bash
chmod +x infra/scripts/deploy-prod.sh
./infra/scripts/deploy-prod.sh
```

4. 安装 Nginx 配置：

```bash
cp infra/nginx/gemshin_nb.conf /etc/nginx/conf.d/gemshin_nb.conf
nginx -t
systemctl reload nginx
```

5. 验证健康检查：

```bash
curl http://127.0.0.1:8100/api/v1/health/
curl http://991hahahanxsm.xyz/api/v1/health/
```

6. 验证产品登录：

```text
https://991hahahanxsm.xyz/login
```

产品后台账号使用 `.env.production` 中的 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 登录。

如需运维排查，也可以访问 Django Admin：

```text
https://991hahahanxsm.xyz/admin/
```

## HTTPS

当前 Nginx 模板只声明 HTTP server block。生产正式开放时，需要在服务器上为 `991hahahanxsm.xyz` 签发证书，并让 Nginx 将 HTTP 跳转到 HTTPS。

如果使用 Certbot，先确认现有 `multica.991hahahanxsm.xyz` 证书配置不会被覆盖，再给根域名单独签发证书。

## 后续更新

```bash
git pull
./infra/scripts/deploy-prod.sh
```

迁移由部署脚本执行：

```bash
python manage.py migrate
```

静态文件由部署脚本收集：

```bash
python manage.py collectstatic --noinput
```
