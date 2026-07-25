import type { ModuleInfo } from "~/services/moduleApi"
import { createModuleApi } from "~/services/moduleApi"

export const useModules = () => {
  const { authorizedFetch } = useAuth()
  const modules = useState<ModuleInfo[]>("modules", () => [])
  const loading = useState<boolean>("modules-loading", () => false)
  const error = useState<string | null>("modules-error", () => null)

  const moduleApi = createModuleApi(authorizedFetch)

  const fetchModules = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await moduleApi.listModules()
      modules.value = response.modules
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "获取模块列表失败"
      error.value = message
      modules.value = []
    } finally {
      loading.value = false
    }
  }

  const getModule = async (code: string) => {
    try {
      return await moduleApi.getModule(code)
    } catch {
      return null
    }
  }

  return {
    modules,
    loading,
    error,
    fetchModules,
    getModule,
  }
}
