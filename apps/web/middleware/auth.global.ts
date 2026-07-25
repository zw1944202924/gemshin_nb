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

  // 强制改密：已登录且 must_change_password 时，只能访问个人中心
  if (token.value && user.value?.must_change_password && to.path !== "/profile") {
    return navigateTo("/profile")
  }

  // 管理员页面权限检查
  if (to.path === "/account" && token.value && user.value && !user.value.is_admin) {
    return navigateTo("/profile")
  }
})