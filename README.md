# gemshin_nb
一个伟大的项目

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
