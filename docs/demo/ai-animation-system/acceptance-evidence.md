# AI动画制作系统 Demo 验收清单

## 验收对象

- `module-center-entry-demo.html`
- `system-home-demo.html`
- `project-workbench-demo.html`
- `shot-refine-demo.html`
- `information-architecture.md`

## 旧方案处置结果

- 旧的 `creation-space / current-work / asset-library / task-history` 四页扁平同级方案不再保留在本分支
- `creation-space` 收敛为系统级的 `system-home`
- `current-work` 拆为 `project-workbench` 与 `shot-refine`
- `asset-library` 与 `task-history` 不再单独占据同级业务导航，改为全局 / 项目 / 镜头三级归属

## 浏览器级验收凭证

- 生成时间：`2026-07-12 16:59`（Asia/Shanghai）
- 生成方式：本地静态服务加载 `docs/demo/ai-animation-system/*.html` 后，用 Playwright 生成 PNG 截图

### 桌面端截图

- `evidence/desktop-module-center-entry.png`
- `evidence/desktop-system-home.png`
- `evidence/desktop-project-workbench.png`
- `evidence/desktop-shot-refine.png`

四张桌面端截图尺寸均为 `1440 x 1600`

### 窄屏截图

- `evidence/mobile-module-center-entry.png`
- `evidence/mobile-system-home.png`
- `evidence/mobile-project-workbench.png`
- `evidence/mobile-shot-refine.png`

窄屏截图尺寸如下：

- `mobile-module-center-entry.png`：`390 x 1809`
- `mobile-system-home.png`：`390 x 2459`
- `mobile-project-workbench.png`：`390 x 3417`
- `mobile-shot-refine.png`：`390 x 2961`

## 层级与跳转核对结果

### `module-center-entry-demo.html`

- 平台顶栏保留 `首页 / 模块中心 / AI 助手 / 个人中心 / 账户与权限`
- `AI动画制作系统` 作为模块卡片被发现和进入
- 主动作 `进入 AI动画制作系统 / 查看系统首页` 均跳转到 `system-home-demo.html`

### `system-home-demo.html`

- 面包屑处于 `gemshin_nb / 模块中心 / AI动画制作系统`
- 系统导航固定为 `系统首页 / 全局素材 / 全局任务 / 系统设置`
- `继续《海港追光》` 与 `项目总览` 均跳转到 `project-workbench-demo.html`

### `project-workbench-demo.html`

- 面包屑进入项目层：`... / AI动画制作系统 / 海港追光`
- 顶部同时保留系统导航与项目导航
- 项目导航固定为 `项目总览 / 章节分镜 / 项目素材 / 项目任务 / 导出`
- `继续镜头 27 / 打开镜头 27 / 进入精修` 均跳转到 `shot-refine-demo.html`

### `shot-refine-demo.html`

- 面包屑进入镜头层：`... / 海港追光 / 第三章 / 镜头 27`
- 保留系统导航与项目导航，不再新增第四套一级导航
- `返回项目工作台` 与 `查看项目任务` 均回到项目层对应落点

## 主要状态核对结果

- 模块中心入口：区分 `已开放 / 开发中` 模块状态
- 系统首页：区分最近项目、全局任务、全局素材三类系统级对象
- 项目工作台：区分章节进度、当前镜头、项目任务阻塞、项目素材待确认
- 镜头精修层：区分镜头版本、镜头素材挂接、镜头任务失败 / 待重跑

## 响应式与溢出核对结果

- 四页均生成桌面端与 `390px` 窄屏截图
- 抽查 `desktop-system-home.png` 与 `mobile-shot-refine.png`，确认首屏正常加载，不是空白页或错位截图
- 窄屏下顶栏仍为横向可滚动结构，系统导航与项目导航保持可见
- 窄屏下项目工作台与镜头精修均转为单列主流程，不再保留三栏并排
- 通过 Playwright 窄屏断言核对 `topnav`、`subnav` 及项目页 `project-nav` 的存在性，执行通过
- 窄屏断言同时检查 `documentElement.scrollWidth <= innerWidth`，未出现横向溢出失败

## Git 验收范围

- 本轮只允许在长期分支 `ai-animation-alignment` 上落改动
- 不创建 PR
- 不合并 `dev`

## 复核建议

先看 `information-architecture.md`，再按以下顺序核图：

1. `desktop-module-center-entry.png`
2. `desktop-system-home.png`
3. `desktop-project-workbench.png`
4. `desktop-shot-refine.png`
5. 对照四张 `mobile-*.png` 看层级在窄屏下是否仍然成立
