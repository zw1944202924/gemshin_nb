const SENSITIVE_DETAIL_MARKERS = ["password", "hash", "secret", "token", "credential"]
const DETAIL_LABELS: Record<string, string> = {
  fields: "修改字段",
  old_roles: "原角色",
  new_roles: "新角色",
  roles: "分配角色",
  must_change_password: "下次登录需改密"
}

const FIELD_LABELS: Record<string, string> = {
  display_name: "显示名称",
  email: "邮箱"
}

export interface AuditLogItem {
  action?: string
  summary?: string
  created_at?: string
  result?: string
  detail?: Record<string, any>
}

function isSensitiveKey(key: string) {
  const lowerKey = key.toLowerCase()
  if (lowerKey === "must_change_password") {
    return false
  }
  return SENSITIVE_DETAIL_MARKERS.some(marker => lowerKey.includes(marker))
}

function formatDetailValue(key: string, value: unknown) {
  if (Array.isArray(value)) {
    const items = key === "fields"
      ? value.map(item => FIELD_LABELS[String(item)] || String(item))
      : value.map(item => String(item))
    return items.length ? items.join("、") : "无"
  }

  if (typeof value === "boolean") {
    return value ? "是" : "否"
  }

  if (value === null || value === undefined || value === "") {
    return "无"
  }

  return String(value)
}

export function getAuditDetailRows(log: AuditLogItem) {
  const detail = log.detail || {}
  const orderedKeys = ["fields", "old_roles", "new_roles", "roles", "must_change_password"]

  return orderedKeys
    .filter(key => key in detail && !isSensitiveKey(key))
    .map(key => `${DETAIL_LABELS[key] || key}：${formatDetailValue(key, detail[key])}`)
}

export function getAuditSummary(log: AuditLogItem) {
  return log.summary || "未提供审计摘要"
}

export function getAuditResultLabel(result?: string) {
  return result === "success" || !result ? "成功" : "失败"
}
