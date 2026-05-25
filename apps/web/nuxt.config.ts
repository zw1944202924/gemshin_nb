export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ["~/assets/main.css"],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api/v1"
    }
  },
  compatibilityDate: "2025-01-01"
})
