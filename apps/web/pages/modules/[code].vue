<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true,
})

const route = useRoute()
const code = route.params.code as string

const { getModule } = useModules()
const module = ref<Awaited<ReturnType<typeof getModule>>>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  loading.value = true
  const result = await getModule(code)
  if (result) {
    module.value = result
  } else {
    error.value = "无权访问该模块或模块不存在"
  }
  loading.value = false
})
</script>

<template>
  <div class="module-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">🔒</div>
      <h1 class="error-title">无法访问</h1>
      <p class="error-desc">{{ error }}</p>
      <NuxtLink to="/modules" class="back-link">返回模块中心</NuxtLink>
    </div>

    <!-- 模块详情占位 -->
    <div v-else-if="module" class="placeholder-page">
      <section class="placeholder-hero">
        <div class="placeholder-hero-inner">
          <div class="module-icon-large">{{ module.icon || '📦' }}</div>
          <p class="kicker">功能准备中</p>
          <h1>{{ module.name }}</h1>
          <p class="hero-desc">
            {{ module.description }}
          </p>
          <p class="hero-note">
            该模块的内部业务功能正在开发中，即将上线。当前阶段仅建设平台侧模块选择与授权能力。
          </p>
          <NuxtLink to="/modules" class="back-link">返回模块中心</NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.module-detail {
  min-height: 100vh;
}

.loading-state {
  text-align: center;
  padding: 80px 24px;
  color: var(--ink-muted);
  font-size: 15px;
}

.error-state {
  text-align: center;
  padding: 80px 24px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 24px;
}

.error-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--ink-primary);
  margin-bottom: 12px;
}

.error-desc {
  max-width: 48ch;
  margin: 0 auto;
  color: var(--ink-copy);
  line-height: 1.7;
  font-size: 15px;
}

.placeholder-page {
  min-height: 100vh;
}

.placeholder-hero {
  padding: 80px 24px;
  position: relative;
}

.placeholder-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(114, 162, 255, 0.08), transparent 40%);
  pointer-events: none;
}

.placeholder-hero-inner {
  position: relative;
  z-index: 1;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  text-align: center;
}

.module-icon-large {
  font-size: 64px;
  margin-bottom: 24px;
}

.kicker {
  margin: 0 0 12px;
  color: var(--ink-accent);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.placeholder-hero-inner h1 {
  font-size: clamp(32px, 5vw, 48px);
  line-height: 1.08;
  letter-spacing: -0.03em;
  text-wrap: balance;
}

.hero-desc {
  max-width: 50ch;
  margin: 16px auto 0;
  color: var(--ink-copy);
  font-size: 16px;
  line-height: 1.7;
}

.hero-note {
  max-width: 50ch;
  margin: 12px auto 0;
  color: var(--ink-muted);
  font-size: 14px;
  line-height: 1.6;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  margin-top: 32px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #081120;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.15s;
}

.back-link:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}
</style>
