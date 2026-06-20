<script setup lang="ts">
const workflowSteps = [
  { name: "导入", detail: "导入小说正文、章节或梗概，建立项目起点。" },
  { name: "整理", detail: "提取角色、场景和剧情摘要，确认结构化内容。" },
  { name: "生成", detail: "进入漫剧工作台，持续推进分镜、素材和配音。" },
  { name: "校验", detail: "识别缺口、失败任务和依赖失效，避免盲目导出。" },
  { name: "导出", detail: "输出结构化产物包，带着完整度判断继续后续工作。" }
]

const pageHighlights = [
  { title: "项目中心", summary: "先看到最近项目、阶段进度和待处理项，而不是空欢迎页。", to: "/modules/projects" },
  { title: "漫剧工作台", summary: "左侧阶段导航，中间主工作区，右侧状态与缺口说明。", to: "/modules/workbench" },
  { title: "结果校验与导出", summary: "先判断是否可导出，再决定补缺口还是直接输出。", to: "/modules/validation" }
]

const valuePoints = [
  "项目驱动，而不是一次性生成",
  "阶段推进，而不是堆功能入口",
  "结果可导出，也可回退补缺口"
]
</script>

<template>
  <main class="landing-page">
    <!-- Hero 区域 -->
    <section class="hero">
      <div class="hero-grid">
        <div class="hero-copy">
          <p class="kicker">面向长期生产的人机协同工作台</p>
          <h1>不是再做一个 AI 工具页，而是做一个真正能推进项目的生产界面。</h1>
          <p class="hero-intro">
            gemshin_nb 把内容导入、整理、生成、校验和导出组织成稳定主链路。
            首页先建立产品感，登录后直接进入工作台，而不是让用户在模板式页面里找入口。
          </p>

          <div class="hero-actions">
            <NuxtLink to="/modules/projects" class="btn-primary btn-large">进入项目中心</NuxtLink>
            <a href="#workflow" class="btn-secondary">查看工作流</a>
          </div>

          <ul class="hero-chips">
            <li v-for="item in valuePoints" :key="item">{{ item }}</li>
          </ul>
        </div>

        <!-- 产品壳预览 -->
        <section class="mockup" aria-label="登录后产品壳预览">
          <div class="mockup-top">
            <div class="mockup-dots" aria-hidden="true">
              <span /><span /><span />
            </div>
            <div class="mockup-title">gemshin_nb / 漫剧项目 021</div>
            <div class="mockup-status">项目中心</div>
          </div>

          <div class="mockup-body">
            <aside class="nav-panel">
              <div class="panel-label">阶段导航</div>
              <ul class="stage-list">
                <li class="active">导入</li>
                <li>整理</li>
                <li>生成</li>
                <li>校验</li>
                <li>导出</li>
              </ul>
            </aside>

            <section class="workbench">
              <div class="stat-strip">
                <span>最近项目</span>
                <span>3 个待处理</span>
                <span>1 个失败</span>
              </div>

              <article class="hero-card">
                <div>
                  <div class="card-label">漫剧工作台</div>
                  <strong>当前卡在视频生成，依赖 2 个镜头素材待更新</strong>
                </div>
                <button type="button">继续处理</button>
              </article>

              <div class="info-grid">
                <article class="info-card">
                  <div class="card-label">内容导入</div>
                  <strong>小说正文已解析</strong>
                  <p>3 章待确认结构化结果</p>
                </article>
                <article class="info-card">
                  <div class="card-label">结果校验</div>
                  <strong>导出缺口 4 项</strong>
                  <p>2 个配音缺失，2 个视频失效</p>
                </article>
              </div>
            </section>

            <aside class="status-panel">
              <div class="panel-label">状态侧栏</div>
              <div class="status-stack">
                <article class="status-card warning">
                  <strong>导出暂不可用</strong>
                  <p>需要先补齐音频与视频缺口</p>
                </article>
                <article class="status-card">
                  <strong>处理建议</strong>
                  <p>先补失败镜头，再重新触发校验</p>
                </article>
              </div>
            </aside>
          </div>
        </section>
      </div>
    </section>

    <!-- 工作流区域 -->
    <section id="workflow" class="content-section">
      <div class="section-heading">
        <h2>工作流不是装饰，而是首页的主要叙事。</h2>
        <p>用户要在很短时间里知道自己进来以后会经历什么，以及系统到底帮他推进哪条链路。</p>
      </div>

      <div class="workflow-grid">
        <article v-for="step in workflowSteps" :key="step.name" class="workflow-card">
          <strong>{{ step.name }}</strong>
          <p>{{ step.detail }}</p>
        </article>
      </div>
    </section>

    <!-- 页面预览区域 -->
    <section id="pages" class="content-section">
      <div class="section-heading">
        <h2>首页负责建立气质，内部页面负责把事做完。</h2>
        <p>这 3 个代表页面是同一套产品结构的延续，不会出现首页一个世界、登录后另一个世界。</p>
      </div>

      <div class="page-grid">
        <NuxtLink v-for="page in pageHighlights" :key="page.title" :to="page.to" class="page-card">
          <span>{{ page.title }}</span>
          <p>{{ page.summary }}</p>
        </NuxtLink>
      </div>
    </section>

    <!-- 设计说明区域 -->
    <section id="why" class="content-section why-section">
      <div class="why-copy">
        <h2>这版实现想验证的不是"好不好看"，而是"有没有正式产品感"。</h2>
        <p>
          视觉上采用深色首屏、强标题、少量说明和真实界面预览，避免落回模板式 Hero。
          结构上把首页入口与登录后工作台连成一条连续路径，让用户从第一眼到真正开始工作都在同一套产品语境里。
        </p>
      </div>

      <div class="why-notes">
        <div class="note-card">
          <strong>避免什么</strong>
          <p>单 Hero 承载全部信息、渐变卡片堆叠、技术栈抢首屏、过度营销化文案。</p>
        </div>
        <div class="note-card">
          <strong>保留什么</strong>
          <p>强首屏、明确主按钮、稳定工作流、登录后统一产品壳，以及任务导向的状态反馈。</p>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
}

/* ── Hero 区域 ── */
.hero {
  position: relative;
  overflow: hidden;
  padding: 22px 20px 84px;
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(114, 162, 255, 0.1), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 22%);
  pointer-events: none;
}

.hero-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(400px, 560px);
  gap: 48px;
  align-items: center;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding-top: 72px;
}

.hero-copy {
  max-width: 620px;
}

.kicker {
  margin: 0 0 14px;
  color: var(--ink-accent);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-copy h1 {
  max-width: 14ch;
  font-size: clamp(48px, 7vw, 80px);
  line-height: 0.94;
  letter-spacing: -0.04em;
  text-wrap: balance;
  color: var(--ink-primary);
}

.hero-intro {
  max-width: 58ch;
  margin-top: 20px;
  color: var(--ink-copy);
  font-size: 17px;
  line-height: 1.85;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 32px;
}

.btn-large {
  min-height: 56px;
  padding: 0 28px;
  font-size: 16px;
  border-radius: 14px;
}

.hero-chips {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  list-style: none;
  padding: 0;
  margin: 28px 0 0;
}

.hero-chips li {
  padding: 10px 16px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-light);
  background: rgba(7, 17, 31, 0.36);
  color: rgba(237, 244, 255, 0.82);
  font-size: 14px;
}

/* ── Mockup 预览 ── */
.mockup {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: linear-gradient(180deg, rgba(19, 31, 51, 0.98), rgba(12, 21, 35, 0.98));
  box-shadow: var(--shadow-float);
}

.mockup-top {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(188, 209, 248, 0.12);
}

.mockup-dots {
  display: flex;
  gap: 6px;
}

.mockup-dots span {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  background: rgba(214, 226, 246, 0.32);
}

.mockup-title,
.mockup-status {
  font-size: 13px;
  color: rgba(234, 241, 255, 0.8);
}

.mockup-status {
  color: rgba(191, 214, 255, 0.78);
}

.mockup-body {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr) 160px;
  min-height: 480px;
}

.nav-panel,
.status-panel {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
}

.nav-panel {
  border-right: 1px solid rgba(188, 209, 248, 0.1);
}

.status-panel {
  border-left: 1px solid rgba(188, 209, 248, 0.1);
}

.panel-label,
.card-label {
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(205, 220, 247, 0.66);
}

.stage-list {
  display: grid;
  gap: 8px;
  list-style: none;
  padding: 12px 0 0;
  margin: 0;
}

.stage-list li {
  padding: 11px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(233, 241, 255, 0.76);
  font-size: 13px;
}

.stage-list li.active {
  background: var(--accent-gradient);
  color: #09111f;
  font-weight: 600;
}

.workbench {
  display: grid;
  gap: 12px;
  padding: 16px;
  align-content: start;
}

.stat-strip {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stat-strip span {
  padding: 6px 10px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(233, 241, 255, 0.72);
  font-size: 12px;
}

.hero-card,
.info-card,
.status-card {
  border-radius: 14px;
  padding: 14px;
}

.hero-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  background: linear-gradient(135deg, rgba(90, 137, 222, 0.24), rgba(15, 28, 49, 0.18));
  border: 1px solid var(--border-accent);
}

.hero-card strong,
.info-card strong,
.status-card strong {
  display: block;
  margin-top: 6px;
  line-height: 1.5;
  color: rgba(247, 250, 255, 0.96);
  font-size: 14px;
  font-weight: 600;
}

.hero-card button {
  border: 0;
  border-radius: 12px;
  padding: 10px 14px;
  background: rgba(244, 248, 255, 0.94);
  color: #091220;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-card,
.status-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
}

.info-card p,
.status-card p {
  margin-top: 6px;
  color: rgba(214, 225, 242, 0.68);
  line-height: 1.5;
  font-size: 12px;
}

.status-stack {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.status-card.warning {
  background: var(--warning-bg);
}

/* ── 内容区域 ── */
.content-section {
  position: relative;
  z-index: 1;
  padding: 80px 0;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
}

.section-heading {
  margin-bottom: 36px;
}

.section-heading h2 {
  max-width: 18ch;
  font-size: clamp(30px, 4vw, 48px);
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: var(--surface-ink);
  text-wrap: balance;
}

.section-heading p {
  max-width: 60ch;
  margin-top: 14px;
  color: var(--surface-copy);
  line-height: 1.8;
  font-size: 16px;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.workflow-card {
  padding: 22px;
  border-radius: 18px;
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  box-shadow: var(--shadow-card);
}

.workflow-card strong {
  display: block;
  color: var(--surface-ink);
  font-size: 17px;
  font-weight: 700;
}

.workflow-card p {
  margin-top: 10px;
  color: var(--surface-copy);
  line-height: 1.7;
  font-size: 14px;
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.page-card {
  padding: 22px;
  border-radius: 18px;
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  box-shadow: var(--shadow-card);
  transition: transform 0.2s, box-shadow 0.2s;
  display: block;
}

.page-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 48px rgba(12, 18, 29, 0.14);
}

.page-card span {
  display: block;
  color: var(--surface-ink);
  font-size: 18px;
  font-weight: 700;
}

.page-card p {
  margin-top: 8px;
  color: var(--surface-copy);
  line-height: 1.7;
  font-size: 14px;
}

/* ── Why 区域 ── */
.why-section {
  padding-bottom: 100px;
}

.why-copy {
  max-width: 720px;
}

.why-copy h2 {
  font-size: clamp(28px, 3.5vw, 42px);
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: var(--surface-ink);
  text-wrap: balance;
}

.why-copy p {
  margin-top: 14px;
  color: var(--surface-copy);
  line-height: 1.8;
  font-size: 16px;
}

.why-notes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 36px;
}

.note-card {
  padding: 24px;
  border-radius: 18px;
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  box-shadow: var(--shadow-card);
}

.note-card strong {
  display: block;
  color: var(--surface-ink);
  font-size: 17px;
  font-weight: 700;
}

.note-card p {
  margin-top: 8px;
  color: var(--surface-copy);
  line-height: 1.7;
  font-size: 14px;
}

/* ── 响应式 ── */
@media (max-width: 1140px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 36px;
  }

  .hero-copy {
    max-width: none;
  }

  .mockup-body {
    grid-template-columns: 1fr;
  }

  .nav-panel {
    border-right: 0;
    border-bottom: 1px solid rgba(188, 209, 248, 0.1);
  }

  .status-panel {
    border-left: 0;
    border-top: 1px solid rgba(188, 209, 248, 0.1);
  }
}

@media (max-width: 820px) {
  .hero-copy h1 {
    max-width: none;
    font-size: clamp(38px, 10vw, 60px);
  }

  .hero-card {
    grid-template-columns: 1fr;
  }

  .why-notes {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-actions,
  .hero-chips {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .mockup {
    border-radius: 20px;
  }

  .workflow-grid,
  .page-grid {
    grid-template-columns: 1fr;
  }
}
</style>
