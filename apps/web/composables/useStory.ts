import type {
  StoryProject,
  StoryShot,
  StoryJob,
  StoryJobSummary,
  ExportSummary,
  ExportValidation,
  ProjectStatus,
} from "~/services/storyApi"

export const useStory = () => {
  const { authorizedFetch } = useAuth()

  const projects = useState<StoryProject[]>("story-projects", () => [])
  const activeProject = useState<StoryProject | null>("story-active-project", () => null)
  const shots = useState<StoryShot[]>("story-shots", () => [])
  const activeShot = useState<StoryShot | null>("story-active-shot", () => null)
  const jobs = useState<StoryJobSummary[]>("story-jobs", () => [])
  const activeJob = useState<StoryJob | null>("story-active-job", () => null)
  const exportSummary = useState<ExportSummary | null>("story-export-summary", () => null)
  const exportValidation = useState<ExportValidation | null>("story-export-validation", () => null)
  const loading = useState<boolean>("story-loading", () => false)
  const error = useState<string | null>("story-error", () => null)

  const clearError = () => {
    error.value = null
  }

  const fetchProjects = async (status?: ProjectStatus) => {
    loading.value = true
    clearError()
    try {
      const params = status ? `?status=${status}` : ""
      const data = await authorizedFetch<StoryProject[]>(`/story/projects/${params}`)
      projects.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "加载项目列表失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const createProject = async (title: string, description = "", config?: Record<string, unknown>) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryProject>("/story/projects/", {
        method: "POST",
        body: { title, description, config },
      })
      projects.value = [data, ...projects.value]
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "创建项目失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchProject = async (projectId: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryProject>(`/story/projects/${projectId}/`)
      activeProject.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "加载项目失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateProject = async (projectId: number, payload: Record<string, unknown>) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryProject>(`/story/projects/${projectId}/`, {
        method: "PATCH",
        body: payload,
      })
      activeProject.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "更新项目失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchShots = async (projectId: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryShot[]>(`/story/projects/${projectId}/shots/`)
      shots.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "加载分镜列表失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const createShot = async (projectId: number, order: number, description = "", settings?: Record<string, unknown>) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryShot>(`/story/projects/${projectId}/shots/`, {
        method: "POST",
        body: { order, description, settings },
      })
      shots.value = [...shots.value, data]
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "创建分镜失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchShot = async (shotId: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryShot>(`/story/shots/${shotId}/`)
      activeShot.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "加载分镜失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateShot = async (shotId: number, payload: Record<string, unknown>) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryShot>(`/story/shots/${shotId}/`, {
        method: "PATCH",
        body: payload,
      })
      activeShot.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "更新分镜失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchJobs = async (projectId: number, shotId?: number, jobType?: string) => {
    loading.value = true
    clearError()
    try {
      const params = new URLSearchParams()
      if (shotId !== undefined) params.set("shot_id", String(shotId))
      if (jobType) params.set("job_type", jobType)
      const qs = params.toString() ? `?${params.toString()}` : ""
      const data = await authorizedFetch<StoryJobSummary[]>(`/story/projects/${projectId}/jobs/${qs}`)
      jobs.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "加载任务列表失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const createJob = async (projectId: number, jobType: string, shotId?: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryJob>(`/story/projects/${projectId}/jobs/`, {
        method: "POST",
        body: { job_type: jobType, shot_id: shotId },
      })
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "创建任务失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchJob = async (jobId: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryJob>(`/story/jobs/${jobId}/`)
      activeJob.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "加载任务失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const retryJob = async (jobId: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<StoryJob>(`/story/jobs/${jobId}/retry/`, {
        method: "POST",
      })
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "重试任务失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchExportSummary = async (projectId: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<ExportSummary>(`/story/projects/${projectId}/export-summary/`)
      exportSummary.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "加载导出摘要失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchExportValidation = async (projectId: number) => {
    loading.value = true
    clearError()
    try {
      const data = await authorizedFetch<ExportValidation>(`/story/projects/${projectId}/export-validate/`)
      exportValidation.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.error || e?.statusMessage || "导出校验失败"
      throw e
    } finally {
      loading.value = false
    }
  }

  const downloadExport = async (projectId: number) => {
    const { token, user } = useAuth()
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase

    if (!token.value || !user.value) {
      error.value = "未登录"
      return
    }

    const response = await $fetch<Blob>(`${apiBase}/story/projects/${projectId}/export-download/`, {
      headers: { Authorization: `Bearer ${token.value}` },
      responseType: "blob",
    })

    const url = URL.createObjectURL(response)
    const a = document.createElement("a")
    a.href = url
    a.download = "export.zip"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return {
    projects,
    activeProject,
    shots,
    activeShot,
    jobs,
    activeJob,
    exportSummary,
    exportValidation,
    loading,
    error,
    clearError,
    fetchProjects,
    createProject,
    fetchProject,
    updateProject,
    fetchShots,
    createShot,
    fetchShot,
    updateShot,
    fetchJobs,
    createJob,
    fetchJob,
    retryJob,
    fetchExportSummary,
    fetchExportValidation,
    downloadExport,
  }
}
