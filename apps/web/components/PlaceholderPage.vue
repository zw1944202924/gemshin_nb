<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="placeholder-page">
    <section class="placeholder-hero">
      <div class="placeholder-hero-inner">
        <p class="kicker">功能准备中</p>
        <h1>{{ title }}</h1>
        <p class="hero-desc">
          {{ description || "此页面正在开发中，即将上线。" }}
        </p>
        <NuxtLink to="/" class="back-link">返回首页</NuxtLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
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