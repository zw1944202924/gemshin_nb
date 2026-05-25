# gemshin_nb

面向长期扩展、便于人和 agent 协同开发的产品底座项目。当前阶段先收敛基础架构方案与第一阶段落地范围，再逐步补齐实现。

## 项目定位

这个仓库不是一次性拼装的 demo，而是后续可以持续演进的业务底座。当前已经确定的目标是：

- 前端采用 Vue 生态，优先使用 Nuxt
- 后端采用 Django / Django REST Framework
- 数据库采用 MySQL
- 缓存与异步任务基础设施采用 Redis，后续预留 Celery 接入位
- 不从零生搭，而是基于成熟骨架整合出适合本项目的长期基线

## 当前技术决策

### 前端

- 起步骨架：`nuxt-ui-templates/dashboard`
- 组件体系：`nuxt/ui`

这样选择的原因是 `dashboard` 本身就建立在 `Nuxt UI` 之上，适合作为一个可直接起跑的管理后台/业务系统骨架，后续扩展时也能持续沿用同一套组件体系。

### 后端

- 起步参考：`cookiecutter-django-mysql`

这样选择的原因是它能快速提供 Django + MySQL 的基础工程结构，但它只是起步参考，不直接等同于长期基线。后续落地时需要对 Python、Django、依赖版本、Docker 配置、认证方式和 DRF 组织方式做一次现代化校准。

## 仓库组织方向

本项目按 monorepo 思路推进，目标结构如下：

```text
repo-root/
  apps/
    web/              # Nuxt 应用
    api/              # Django / DRF 应用
  packages/
    shared-types/     # 前后端共享类型、枚举、接口约定
    eslint-config/    # 前端共享配置
  infra/
    docker/
    scripts/
  docs/
    architecture/
    api/
    onboarding/
  .env.example
  docker-compose.yml
  Makefile
  README.md
```

说明：

- `apps` 保持前后端边界清晰，便于并行开发
- `packages` 只放真正需要复用的共享内容，避免过早耦合
- `infra` 统一容器和脚本
- `docs` 只沉淀本项目自己的架构、接口和协作约定

## 第一阶段目标

第一阶段只做最小可运行底座，不追求一次性做全：

- Web 端 dashboard 跑起来，并替换成项目自己的导航与首页
- API 端 Django / DRF 跑起来
- MySQL、Redis、本地 `docker compose` 跑通
- 建立一个完整认证闭环
- 做一个示例业务模块，优先考虑 `projects`、`tasks` 或 `notes`
- 补齐 `README`、环境变量说明和启动步骤
- 定下基础代码规范与协作方式

示例业务模块的作用不是追求业务复杂度，而是先把这些链路跑通：

- 数据模型
- Django Admin
- DRF serializer / viewset
- 前端列表页 / 详情页 / 表单页
- 权限控制
- 错误处理
- 基础日志与测试

## 接口与开发约定

- 后端接口统一使用 `/api/v1/...`
- 前端通过一层服务封装访问接口，不在页面里直接散落请求逻辑
- OpenAPI 可以作为后续目标，但第一阶段不要求先生成全量 SDK
- 默认开发方式优先考虑 `docker compose` 启动依赖与后端，前端保留本机开发能力

## README 作用

本 README 只承担项目级说明：

- 这个项目要解决什么问题
- 当前确定的技术方案是什么
- 第一阶段准备做到哪里
- 仓库如何组织、后续如何协作

跨项目复用的方法论或 skill 暂不在这个仓库里展开。

## Git 分支规范

### 分支类型说明

| 分支类型 | 命名规范 | 用途说明 | 生命周期 |
|---------|---------|---------|---------|
| 主分支 | `main` | 生产环境代码，始终保持稳定可发布状态 | 永久 |
| 开发分支 | `dev` | 日常开发集成，包含最新开发特性 | 永久 |
| 功能分支 | `feature/<功能名>` | 开发新功能，从 develop 分支创建 | 临时 |
| 修复分支 | `bugfix/<问题描述>` | 修复开发环境 bug，从 develop 分支创建 | 临时 |
| 发布分支 | `release/<版本号>` | 准备发布新版本，从 develop 分支创建 | 临时 |



### 分支命名示例

```
# 功能分支
feature/user-login
feature/payment-gateway
feature/api-optimization

# 修复分支
bugfix/fix-memory-leak
bugfix/resolve-null-pointer

# 发布分支
release/v1.2.0
release/v2.0.0-beta
```

### 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(auth): 添加用户登录功能

- 实现 JWT Token 认证
- 添加登录接口
- 集成 Redis 缓存

Closes #123
```

### 合并规范

1. **功能开发完成**：`feature/*` → `develop`（通过 Pull Request）
2. **发布新版本**：`develop` → `release/*` → `main` + `develop`
3. **紧急修复**：`hotfix/*` → `main` + `develop`
4. **日常修复**：`bugfix/*` → `develop`

### 注意事项

- 禁止直接向 `main` 分支推送代码
- 所有代码合并必须通过 Pull Request 进行 Code Review
- 合并前确保代码通过所有测试
- 删除已合并的临时分支，保持仓库整洁
