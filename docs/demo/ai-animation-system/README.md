# AI动画制作系统 Demo 目录

本目录承接 `AI动画制作系统` 在 `gemshin_nb` 中的正式信息架构 Demo。当前结构固定为：

`gemshin_nb → 模块中心 → AI动画制作系统 → 项目 → 章节 / 分镜 / 镜头`

本轮只调整系统级导航形式，不改动已经确认的产品层级。平台导航继续留在顶部，`AI动画制作系统` 的系统级模块改为左侧业务侧边栏，项目级导航留在主内容区的上下文带中。

## 范围说明

本轮仅覆盖桌面端场景，不包含移动端、窄屏、抽屉导航和响应式适配。

## 文件清单

- `information-architecture.md`
  - 唯一信息架构对象，说明平台顶栏、系统侧边栏、项目导航和素材/任务归属。
- `demo-theme.css`
  - 四个页面共用的壳层、系统侧边栏、卡片和桌面端样式。
- `module-center-entry-demo.html`
  - 模块中心中的 `AI动画制作系统` 入口，仍属于平台层。
- `system-home-demo.html`
  - `AI动画制作系统` 首页，展示系统侧边栏、项目中心、全局素材、全局任务和系统设置入口。
- `project-workbench-demo.html`
  - 具体项目工作台，保留系统侧边栏，同时在正文里承接项目导航、章节/分镜、项目素材、项目任务和导出。
- `shot-refine-demo.html`
  - 单镜头精修层，保留系统侧边栏，同时在正文里承接项目上下文、镜头编辑、生成参数和镜头任务。
- `acceptance-evidence.md`
  - 桌面端截图、自测结果和 Git 验收说明。
- `evidence/`
  - 桌面端截图文件。

## 推荐阅读顺序

1. `information-architecture.md`
2. `module-center-entry-demo.html`
3. `system-home-demo.html`
4. `project-workbench-demo.html`
5. `shot-refine-demo.html`
6. `acceptance-evidence.md`
