export type ModuleInfo = {
  id: number
  code: string
  name: string
  description: string
  icon: string
  status: string
}

export type ModuleListResponse = {
  modules: ModuleInfo[]
}

export const createModuleApi = (authorizedFetch: <T>(path: string, options?: Record<string, unknown>) => Promise<T>) => ({
  listModules: () => authorizedFetch<ModuleListResponse>("/modules/"),

  getModule: (code: string) => authorizedFetch<ModuleInfo>(`/modules/${code}/`),
})
