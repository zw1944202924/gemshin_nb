# apps/web

当前有效前端目录是 `apps/web`。本目录基于 `main` 分支建立 Nuxt 3 + `@nuxt/ui` 的 dashboard 基线，不依赖旧的 `frontend/` 或 `web_demo/` 目录。

## 当前包含

- `layouts/default.vue`：应用壳层，提供 sidebar、topbar 和主内容区
- `pages/index.vue`：dashboard 起始页，占位当前运行信息和后续扩展位
- `assets/main.css`：全局主题变量、背景和 Nuxt UI 样式入口
- `nuxt.config.ts`：Nuxt UI 模块、受限网络启动策略与运行时 API 基址配置

## 本地开发

```bash
cd apps/web
npm install
npm run dev
```

默认会启动 Nuxt 开发服务器；如果 `3000` 端口被占用，Nuxt 会自动切换到下一个可用端口。
当前配置已经显式关闭 `@nuxt/ui` 默认的远程字体 provider，受限网络下不会再因为访问 Google 字体元数据而卡住首轮启动。

## 本地校验

```bash
cd apps/web
npm run build
```

`build` 通过表示当前 dashboard 基线可作为后续认证、导航和业务模块开发的载体继续扩展。
