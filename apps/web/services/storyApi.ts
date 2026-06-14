export type StoryProject = {
  id: number
  title: string
  description: string
  status: ProjectStatus
  status_display: string
  config: Record<string, unknown>
  shot_count: number
  created_at: string
  updated_at: string
}

export type ProjectStatus = "draft" | "processing" | "completed" | "failed"

export type StoryShot = {
  id: number
  project_id: number
  order: number
  description: string
  status: ShotStatus
  status_display: string
  settings: Record<string, unknown>
  assets: StoryAsset[]
  created_at: string
  updated_at: string
}

export type ShotStatus = "pending" | "processing" | "completed" | "failed"

export type StoryAsset = {
  id: number
  project_id: number
  shot_id: number | null
  asset_type: AssetType
  asset_type_display: string
  file_path: string
  file_size: number
  status: AssetStatus
  status_display: string
  is_stale: boolean
  outdated_by_id: number | null
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export type AssetType = "image" | "video" | "audio" | "subtitle"
export type AssetStatus = "pending" | "processing" | "completed" | "failed" | "stale" | "outdated"

export type StoryJob = {
  id: number
  project_id: number
  shot_id: number | null
  job_type: JobType
  job_type_display: string
  status: JobStatus
  status_display: string
  input_data: Record<string, unknown>
  output_data: Record<string, unknown>
  retry_of_id: number | null
  attempt: number
  started_at: string | null
  completed_at: string | null
  error_message: string
  created_at: string
  updated_at: string
}

export type StoryJobSummary = {
  id: number
  job_type: JobType
  job_type_display: string
  status: JobStatus
  status_display: string
  shot_id: number | null
  attempt: number
  created_at: string
}

export type JobType = "story_outline" | "storyboard" | "image_generation" | "video_generation" | "voice_generation"
export type JobStatus = "pending" | "processing" | "completed" | "failed"

export type ExportShotSummary = {
  shot_id: number
  shot_order: number
  status: string
  assets: Record<string, string>
  missing: string[]
  stale: string[]
  is_complete: boolean
}

export type ExportSummary = {
  project_id: number
  project_title: string
  project_status: string
  shot_count: number
  complete_shots: number
  has_project_subtitles: boolean
  shots: ExportShotSummary[]
}

export type ExportValidation = {
  valid: boolean
  errors: string[]
  summary: ExportSummary
}
