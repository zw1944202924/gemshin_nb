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
- `DJANGO_SUPERUSER_PASSWORD`

生产管理员账号由部署脚本读取 `.env.production` 后自动创建：

```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=1944202924@qq.com
DJANGO_SUPERUSER_PASSWORD=替换为强密码
DJANGO_SUPERUSER_RESET_PASSWORD=0
```

如果管理员账号已存在，部署脚本只会确认它具备 staff/superuser 权限，不会默认重置密码。需要主动重置密码时，临时设置：

```bash
DJANGO_SUPERUSER_RESET_PASSWORD=1
```

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

6. 验证 Django Admin：

```text
https://991hahahanxsm.xyz/admin/
```

使用 `.env.production` 中的 `DJANGO_SUPERUSER_USERNAME` 和 `DJANGO_SUPERUSER_PASSWORD` 登录。

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
