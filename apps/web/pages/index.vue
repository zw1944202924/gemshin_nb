<script setup lang="ts">
const config = useRuntimeConfig()
</script>

<template>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Gemshin Base</p>
      <h1>Nuxt + Django product base</h1>
      <p class="intro">
        This repository now uses a clean monorepo skeleton for the next-generation
        web and API stack.
      </p>
      <div class="panel">
        <p>API base: {{ config.public.apiBase }}</p>
        <ul>
          <li>Web app lives in <code>apps/web</code></li>
          <li>API app lives in <code>apps/api</code></li>
          <li>Infrastructure lives in <code>docker-compose.yml</code> and <code>infra/</code></li>
        </ul>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
}

.hero {
  max-width: 760px;
  background: linear-gradient(135deg, #ffffff, #eef4ff);
  border: 1px solid #d7e2f2;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(22, 32, 51, 0.08);
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #4b6381;
}

h1 {
  margin: 0;
  font-size: clamp(32px, 6vw, 56px);
}

.intro {
  margin: 16px 0 0;
  line-height: 1.6;
}

.panel {
  margin-top: 24px;
  padding: 20px;
  border-radius: 16px;
  background: #162033;
  color: #f5f7fb;
}

code {
  font-family: "SFMono-Regular", Consolas, monospace;
}

ul {
  margin: 12px 0 0;
  padding-left: 20px;
}
</style>
