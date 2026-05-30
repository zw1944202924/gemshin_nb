export default defineNuxtRouteMiddleware(async (to) => {
  const { token, user, refreshSession, clearSession } = useAuth()

  if (token.value && !user.value) {
    try {
      await refreshSession()
    } catch {
      clearSession()
    }
  }

  if (to.meta.requiresAuth && !token.value) {
    return navigateTo(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
  }

  if (to.path === "/login" && token.value) {
    return navigateTo("/dashboard")
  }
})
