# AI动画制作系统 Demo 目录

本目录承接 `AI动画制作系统` 在 `gemshin_nb` 中的正式信息架构 Demo。页面不再使用“创作空间 / 当前作品 / 素材库 / 任务记录”四个扁平同级页面，而是改为：

`gemshin_nb → 模块中心 → AI动画制作系统 → 项目 → 章节 / 分镜 / 镜头`

## 文件清单

- `information-architecture.md`
  - 唯一信息架构对象，说明平台导航、系统导航、项目导航和素材/任务归属。
- `demo-theme.css`
  - 四个页面共用的壳层、卡片、导航、表格和响应式样式。
- `module-center-entry-demo.html`
  - 模块中心中的 `AI动画制作系统` 入口。
- `system-home-demo.html`
  - `AI动画制作系统` 首页，承接项目中心、全局素材、全局任务。
- `project-workbench-demo.html`
  - 具体项目工作台，承接章节/分镜组织、项目素材、项目任务、导出。
- `shot-refine-demo.html`
  - 单镜头精修层，承接镜头编辑、生成参数、镜头任务与结果校验。
- `acceptance-evidence.md`
  - 桌面端与窄屏截图、自测结果和 Git 验收说明。
- `evidence/`
  - 桌面端与窄屏截图文件。

## 推荐阅读顺序

1. `information-architecture.md`
2. `module-center-entry-demo.html`
3. `system-home-demo.html`
4. `project-workbench-demo.html`
5. `shot-refine-demo.html`
6. `acceptance-evidence.md`
