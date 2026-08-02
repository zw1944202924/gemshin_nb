`gemshin_nb` 已提供第一阶段 OIDC 身份提供方能力，`new_api` 应按 Authorization Code + PKCE(S256) 接入。

## Issuer 与端点

- `issuer`: `https://<host>/api/v1/oidc`
- `discovery`: `https://<host>/api/v1/oidc/.well-known/openid-configuration`
- `jwks_uri`: `https://<host>/api/v1/oidc/.well-known/jwks.json`
- `authorization_endpoint`: `https://<host>/api/v1/oidc/authorize/`
- `token_endpoint`: `https://<host>/api/v1/oidc/token/`
- `userinfo_endpoint`: `https://<host>/api/v1/oidc/userinfo/`
- `end_session_endpoint`: `https://<host>/api/v1/oidc/logout/`
- `revocation_endpoint`: `https://<host>/api/v1/oidc/revoke_token/`

## 客户端注册规则

- 通过 Django Admin 创建 `oauth2_provider.Application`。
- `authorization_grant_type` 只允许 `authorization-code`。
- 浏览器、桌面端和移动端统一使用 PKCE `S256`。
- `redirect_uris` 与 `post_logout_redirect_uris` 必须逐条显式登记，不能使用通配符。
- 第一阶段不启用 dynamic client registration，不启用 implicit、hybrid、password、client_credentials。

## 声明契约

- `sub`: 平台内部为每个账号生成的不可变 UUID。消费者必须把它当作唯一外部主体键。
- `preferred_username`: 当前用户名，仅作展示和排障，不能当稳定主键。
- `name`: 显示名，优先 `UserProfile.display_name`，否则回退全名或用户名。
- `email`: 仅在用户资料里存在邮箱时返回。

第一阶段不会下发角色、模块权限或现有内部 Bearer Token。

## 首次账号关联规则

- `new_api` 若已有本地用户表，首次登录时必须优先按 `sub` 建立并持久化绑定。
- 若历史数据还没有 `sub`，可以在受控迁移流程中参考 `preferred_username` 或 `email` 做人工确认，但不能在运行时按可变用户名静默覆盖旧绑定。
- 一旦建立绑定，后续只认 `sub`，用户名变化不视为新账号。

## 会话与失效策略

- 用户改密后，现有平台 Bearer token、OIDC authorization code、access token、refresh token 与浏览器授权会话都会统一失效。
- 管理员重置密码后，目标账号所有现有登录态与 OIDC refresh token 都会失效，必须重新登录。
- 管理员停用账号后，既有 OIDC access/refresh token 和授权浏览器会话立即不可继续使用。
- RP 发起登出时，调用 `end_session_endpoint`，并传 `id_token_hint`、`post_logout_redirect_uri`、`state`。

## 敏感配置边界

- 生产环境必须通过环境变量注入 `OIDC_RSA_PRIVATE_KEY`，不能写入仓库。
- 本地 `DEBUG` 环境允许临时生成开发私钥，但服务重启后旧 `id_token` 会失效。
- 不要在仓库、日志、测试输出或文档里记录真实 `client_secret`、私钥、访问令牌、刷新令牌或数据库连接信息。
