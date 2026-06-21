export default defineNuxtRouteMiddleware(async (to) => {
  const { token, user, refreshSession, clearSession } = useAuth()

  if (token.value && !user.value) {
    try {
      await refreshSession()
    } catch {
      clearSession()
    }
  }

  // 需要登录的页面 → 重定向到首页（首页已集成内联登录表单）
  if (to.meta.requiresAuth && !token.value) {
    return navigateTo(`/?redirect=${encodeURIComponent(to.fullPath)}`)
  }

  // 旧 /login 页面重定向到首页
  if (to.path === "/login") {
    return navigateTo("/")
  }

  // 旧 /dashboard 页面在已登录时保留可用，未登录重定向首页
  if (to.path === "/dashboard" && !token.value) {
    return navigateTo("/")
  }
})