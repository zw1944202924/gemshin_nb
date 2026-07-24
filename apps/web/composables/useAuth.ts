import { resetChatState } from "~/composables/chatState"
import { resetStoryState } from "~/composables/useStory"

type AuthUser = {
  id: number
  username: string
  display_name: string
}

type LoginPayload = {
  username: string
  password: string
}

type LoginResponse = {
  token: string
  expires_in: number
  user: AuthUser
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const token = useCookie<string | null>("gemshin_token", {
    default: () => null
  })
  const user = useState<AuthUser | null>("auth-user", () => null)
  const pending = useState<boolean>("auth-pending", () => false)

  const clearSession = () => {
    resetChatState()
    resetStoryState()
    token.value = null
    user.value = null
  }

  const redirectToLogin = async () => {
    const route = useRoute()
    if (route.path === "/") {
      return
    }

    await navigateTo(`/?redirect=${encodeURIComponent(route.fullPath)}`)
  }

  const authorizedFetch = async <T>(path: string, options: Record<string, unknown> = {}) => {
    if (!token.value) {
      throw createError({ statusCode: 401, statusMessage: "未登录" })
    }

    const headers = {
      ...(options.headers as Record<string, string> | undefined),
      Authorization: `Bearer ${token.value}`
    }

    try {
      return await $fetch<T>(`${config.public.apiBase}${path}`, {
        ...options,
        headers
      })
    } catch (error) {
      const statusCode =
        typeof error === "object" &&
        error !== null &&
        "statusCode" in error &&
        typeof error.statusCode === "number"
          ? error.statusCode
          : null

      if (statusCode === 401) {
        clearSession()
        await redirectToLogin()
      }

      throw error
    }
  }

  const login = async (payload: LoginPayload) => {
    pending.value = true

    try {
      const response = await $fetch<LoginResponse>(`${config.public.apiBase}/auth/login/`, {
        method: "POST",
        body: payload
      })

      token.value = response.token
      user.value = response.user
      return response.user
    } finally {
      pending.value = false
    }
  }

  const refreshSession = async () => {
    if (!token.value) {
      user.value = null
      return null
    }

    try {
      const response = await authorizedFetch<{ user: AuthUser }>("/auth/me/")
      user.value = response.user
      return response.user
    } catch (error) {
      clearSession()
      throw error
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await authorizedFetch<null>("/auth/logout/", { method: "POST" })
      }
    } finally {
      clearSession()
    }
  }

  return {
    token,
    user,
    pending,
    isAuthenticated: computed(() => Boolean(token.value && user.value)),
    authorizedFetch,
    login,
    logout,
    refreshSession,
    clearSession
  }
}
