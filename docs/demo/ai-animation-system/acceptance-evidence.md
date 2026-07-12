# AI动画制作系统 Demo 验收清单

## 验收对象

- `module-center-entry-demo.html`
- `system-home-demo.html`
- `project-workbench-demo.html`
- `shot-refine-demo.html`
- `information-architecture.md`

## 本轮导航调整结果

- 平台顶栏继续保留 `首页 / 模块中心 / AI 助手 / 个人中心 / 账户与权限`
- `AI动画制作系统` 的四个系统级模块改为左侧业务侧边栏：`系统首页 / 全局素材 / 全局任务 / 系统设置`
- 原正文顶部横向 `subnav` 已移除，不再保留重复系统导航
- 进入项目后，系统侧边栏继续存在；项目级导航收回正文中的"当前项目"上下文带
- 未把章节、分镜、镜头、项目素材、项目任务塞进系统侧边栏，与四个系统模块混成一层

## 范围说明

本轮仅覆盖桌面端场景，不包含移动端、窄屏、抽屉导航和响应式验收。

## 浏览器级验收凭证

- 生成时间：`2026-07-12 17:38 CST`
- 生成方式：本地静态页面通过 Playwright 生成桌面端 PNG 截图

### 桌面端截图

- `evidence/desktop-module-center-entry.png`
- `evidence/desktop-system-home.png`
- `evidence/desktop-project-workbench.png`
- `evidence/desktop-shot-refine.png`

桌面端截图尺寸：

- `desktop-module-center-entry.png`：`1440 x 1600`
- `desktop-system-home.png`：`1440 x 1600`
- `desktop-project-workbench.png`：`1440 x 1803`
- `desktop-shot-refine.png`：`1440 x 1600`

## 层级与跳转核对结果

### `module-center-entry-demo.html`

- 保持平台层入口，不提前出现系统侧边栏
- `进入 AI动画制作系统 / 查看系统首页` 均进入 `system-home-demo.html`

### `system-home-demo.html`

- 平台顶栏和系统侧边栏分层明确
- 左侧固定 `系统首页 / 全局素材 / 全局任务 / 系统设置 / 返回模块中心`
- `继续《海港追光》` 进入 `project-workbench-demo.html`

### `project-workbench-demo.html`

- 左侧保留系统侧边栏，随时可回到系统级模块
- 项目名称和项目导航位于正文上下文带，不进入系统侧边栏
- `继续镜头 27 / 打开镜头 27 / 进入精修` 均跳转到 `shot-refine-demo.html`

### `shot-refine-demo.html`

- 左侧仍保留系统侧边栏
- 项目导航位于正文上下文带，镜头上下文通过面包屑和章节内镜头列表表达
- `查看项目任务` 返回项目层对应区域

## 主要状态核对结果

- 系统侧边栏具备当前模块选中态
- 系统首页区分最近项目、全局任务、全局素材和系统设置入口
- 项目工作台区分章节进度、当前镜头、项目任务阻塞、项目素材待确认
- 镜头精修层区分镜头版本、镜头素材挂接、镜头任务失败 / 待重跑

## 自测清单

- `rg -n "subnav" docs/demo/ai-animation-system/*demo.html` 无结果，确认旧的正文顶部横向系统导航已移除
- 三张系统内页面都包含 `system-sidebar`，项目页和镜头页额外保留 `project-nav`
- 手动复核截图：
  - `desktop-system-home.png`：系统级四个模块只出现在左侧侧边栏，不再横向占据正文顶部
  - `desktop-project-workbench.png`：左侧仍为系统导航，项目导航只留在正文"当前项目"区域
  - `desktop-shot-refine.png`：镜头层未把章节、镜头并入系统侧边栏

## Git 验收范围

- 本轮只允许在长期分支 `ai-animation-alignment` 上落改动
- 不创建 PR
- 不合并 `dev`
