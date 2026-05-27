export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@nuxt/ui"],
  css: ["~/assets/main.css"],
  ui: {
    // 关闭默认远程字体 provider，避免受限网络下 dev 启动阻塞。
    fonts: false
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api/v1"
    }
  },
  compatibilityDate: "2025-01-01"
})
