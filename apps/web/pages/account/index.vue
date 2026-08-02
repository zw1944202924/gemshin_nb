<script setup lang="ts">
import { getAuditDetailRows, getAuditResultLabel, getAuditSummary } from "~/utils/auditLog"

definePageMeta({
  layout: "shell",
  requiresAuth: true
})

const { user, authorizedFetch } = useAuth()
const router = useRouter()

const users = ref([])
const roles = ref([])
const auditLogs = ref([])
const loading = ref(false)
const saving = ref(false)
const message = ref({ type: "", text: "" })
const searchQuery = ref("")

// 审计日志分页
const auditPage = ref(1)
const auditPageSize = ref(10)
const auditTotal = ref(0)
const auditTotalPages = ref(0)

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showResetPasswordModal = ref(false)
const selectedUser = ref(null)

const newUser = ref({
  username: "",
  password: "",
  display_name: "",
  email: "",
  role_ids: [],
  must_change_password: true
})

const resetPasswordForm = ref({
  new_password: "",
  must_change_password: true
})

const isAdmin = computed(() => user.value?.is_admin ?? false)

// 统计数据
const totalUsers = computed(() => users.value.length)
const activeUsers = computed(() => users.value.filter(u => u.is_active).length)
const disabledUsers = computed(() => users.value.filter(u => !u.is_active).length)
const adminUsers = computed(() => users.value.filter(u => u.is_admin).length)

onMounted(async () => {
  if (!isAdmin.value) {
    await navigateTo("/profile")
    return
  }
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    await Promise.all([
      fetchUsers(),
      fetchRoles(),
      fetchAuditLogs()
    ])
  } finally {
    loading.value = false
  }
}

async function fetchUsers() {
  try {
    const params = searchQuery.value ? `?search=${encodeURIComponent(searchQuery.value)}` : ""
    const data = await authorizedFetch(`/accounts/admin/users/${params}`)
    users.value = data.users || []
  } catch (error) {
    message.value = { type: "error", text: "加载用户列表失败" }
  }
}

async function fetchRoles() {
  try {
    const data = await authorizedFetch("/accounts/admin/roles/")
    roles.value = data.roles || []
  } catch (error) {
    console.error("加载角色列表失败", error)
  }
}

async function fetchAuditLogs() {
  try {
    const data = await authorizedFetch(`/accounts/admin/audit-logs/?page=${auditPage.value}&page_size=${auditPageSize.value}`)
    auditLogs.value = data.logs || []
    auditTotal.value = data.pagination?.total || 0
    auditTotalPages.value = data.pagination?.total_pages || 0
  } catch (error) {
    console.error("加载审计日志失败", error)
  }
}

function goToAuditPage(page: number) {
  if (page >= 1 && page <= auditTotalPages.value) {
    auditPage.value = page
    fetchAuditLogs()
  }
}

async function createUser() {
  saving.value = true
  message.value = { type: "", text: "" }
  try {
    await authorizedFetch("/accounts/admin/users/", {
      method: "POST",
      body: newUser.value
    })
    message.value = { type: "success", text: "用户创建成功" }
    showCreateModal.value = false
    newUser.value = {
      username: "",
      password: "",
      display_name: "",
      email: "",
      role_ids: [],
      must_change_password: true
    }
    await fetchUsers()
    await fetchAuditLogs()
  } catch (error: any) {
    const detail = error?.data?.detail || error?.data?.username?.[0] || "创建失败"
    message.value = { type: "error", text: detail }
  } finally {
    saving.value = false
  }
}

async function updateUser() {
  if (!selectedUser.value) return
  
  saving.value = true
  message.value = { type: "", text: "" }
  try {
    await authorizedFetch(`/accounts/admin/users/${selectedUser.value.id}/`, {
      method: "PATCH",
      body: {
        role_ids: selectedUser.value.roles?.map(r => r.id) || [],
        profile: {
          display_name: selectedUser.value.profile?.display_name || "",
          email: selectedUser.value.profile?.email || ""
        }
      }
    })
    message.value = { type: "success", text: "用户更新成功" }
    showEditModal.value = false
    await fetchUsers()
    await fetchAuditLogs()
  } catch (error: any) {
    const detail = error?.data?.detail || "更新失败"
    message.value = { type: "error", text: detail }
  } finally {
    saving.value = false
  }
}

async function disableUser(userId: number) {
  if (!confirm("确定要停用此账号吗？")) return
  
  try {
    await authorizedFetch(`/accounts/admin/users/${userId}/disable/`, {
      method: "POST"
    })
    message.value = { type: "success", text: "账号已停用" }
    await fetchUsers()
    await fetchAuditLogs()
  } catch (error: any) {
    const detail = error?.data?.detail || "停用失败"
    message.value = { type: "error", text: detail }
  }
}

async function enableUser(userId: number) {
  try {
    await authorizedFetch(`/accounts/admin/users/${userId}/enable/`, {
      method: "POST"
    })
    message.value = { type: "success", text: "账号已启用" }
    await fetchUsers()
    await fetchAuditLogs()
  } catch (error: any) {
    const detail = error?.data?.detail || "启用失败"
    message.value = { type: "error", text: detail }
  }
}

async function resetPassword() {
  if (!selectedUser.value) return
  
  saving.value = true
  message.value = { type: "", text: "" }
  try {
    await authorizedFetch(`/accounts/admin/users/${selectedUser.value.id}/reset-password/`, {
      method: "POST",
      body: resetPasswordForm.value
    })
    message.value = { type: "success", text: "密码已重置" }
    showResetPasswordModal.value = false
    resetPasswordForm.value = { new_password: "", must_change_password: true }
    await fetchAuditLogs()
  } catch (error: any) {
    const detail = error?.data?.detail || "重置失败"
    message.value = { type: "error", text: detail }
  } finally {
    saving.value = false
  }
}

function openEditModal(userData: any) {
  selectedUser.value = { ...userData }
  showEditModal.value = true
}

function openResetPasswordModal(userData: any) {
  selectedUser.value = userData
  resetPasswordForm.value = { new_password: "", must_change_password: true }
  showResetPasswordModal.value = true
}

function toggleRole(roleId: number) {
  if (!selectedUser.value) return
  
  const roleIndex = selectedUser.value.roles.findIndex(r => r.id === roleId)
  if (roleIndex >= 0) {
    selectedUser.value.roles.splice(roleIndex, 1)
  } else {
    const role = roles.value.find(r => r.id === roleId)
    if (role) {
      selectedUser.value.roles.push(role)
    }
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return ""
  const date = new Date(dateStr)
  return date.toLocaleString("zh-CN")
}

function getUserInitials(userData: any) {
  const name = userData.profile?.display_name || userData.username || ""
  return name.slice(0, 2).toUpperCase()
}

function getRoleUserCount(roleId: number) {
  return users.value.filter(u => u.roles?.some(r => r.id === roleId)).length
}

watch(searchQuery, () => {
  fetchUsers()
})
</script>

<template>
  <div class="account-page">
    <div class="page-header">
      <div class="header-content">
        <div>
          <p class="page-label">管理员专属</p>
          <h1 class="page-title">账户与权限</h1>
          <p class="page-desc">管理用户账号、角色分配和权限设置。</p>
        </div>
        <button class="btn btn-primary" @click="showCreateModal = true">
          创建账号
        </button>
      </div>
    </div>

    <div v-if="message.text" :class="['alert-banner', `alert-${message.type}`]">
      <div class="alert-icon">{{ message.type === "success" ? "✓" : "!" }}</div>
      <div class="alert-content">{{ message.text }}</div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">总用户数</div>
        <div class="stat-value">{{ totalUsers }}</div>
        <div class="stat-note">已注册账号</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已启用</div>
        <div class="stat-value">{{ activeUsers }}</div>
        <div class="stat-note">正常可用</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已停用</div>
        <div class="stat-value">{{ disabledUsers }}</div>
        <div class="stat-note">无法登录</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">管理员</div>
        <div class="stat-value">{{ adminUsers }}</div>
        <div class="stat-note">拥有管理权限</div>
      </div>
    </div>

    <!-- 用户管理 -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>用户管理</h2>
          <p>管理所有平台账号的状态、角色和密码。操作会记录在审计日志中。</p>
        </div>
        <button class="btn btn-primary" @click="showCreateModal = true">创建账号</button>
      </div>

      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索用户名或显示名称..."
        />
      </div>

      <div class="user-table">
        <div class="user-table-header">
          <div>用户</div>
          <div>状态</div>
          <div>角色</div>
          <div>最近登录</div>
          <div>操作</div>
        </div>

        <div v-if="loading" class="loading-state">加载中...</div>
        
        <div v-else-if="users.length === 0" class="empty-state">
          暂无用户数据
        </div>
        
        <div v-else v-for="userData in users" :key="userData.id" class="user-row">
          <div class="user-name-cell">
            <div class="user-avatar-sm">{{ getUserInitials(userData) }}</div>
            <div>
              <div class="user-name">{{ userData.profile?.display_name || userData.username }}</div>
              <div class="user-email">{{ userData.profile?.email || userData.username }}</div>
            </div>
          </div>
          <div>
            <span :class="['status-badge', userData.is_active ? 'active' : 'disabled']">
              {{ userData.is_active ? "已启用" : "已停用" }}
            </span>
          </div>
          <div class="role-tags">
            <span v-for="role in userData.roles" :key="role.id" :class="['role-tag', { admin: role.code === 'admin' }]">
              {{ role.name }}
            </span>
            <span v-if="!userData.roles?.length" class="text-muted">无角色</span>
          </div>
          <div class="user-last-login">
            {{ formatDate(userData.last_login) || '未登录' }}
          </div>
          <div class="user-actions">
            <button class="btn btn-ghost btn-sm" @click="openEditModal(userData)">编辑</button>
            <button class="btn btn-ghost btn-sm" @click="openResetPasswordModal(userData)">重置密码</button>
            <button
              v-if="userData.is_active"
              class="btn btn-secondary btn-ghost btn-sm"
              :disabled="userData.id === user?.id"
              @click="disableUser(userData.id)"
            >
              停用
            </button>
            <button
              v-else
              class="btn btn-primary btn-ghost btn-sm"
              @click="enableUser(userData.id)"
            >
              启用
            </button>
          </div>
        </div>
      </div>

      <div class="security-notice">
        <div class="security-notice-icon">!</div>
        <div>
          <strong>安全限制：</strong>你不能停用自己的账号，也不能停用最后一个管理员。系统会在操作前自动检查这些条件。
        </div>
      </div>
    </section>

    <!-- 角色管理 -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>角色管理</h2>
          <p>角色是模块访问的唯一来源。用户可同时拥有多个角色，最终可见模块取并集。</p>
        </div>
      </div>

      <div class="role-cards">
        <div v-for="role in roles" :key="role.id" class="role-card">
          <h3><span :class="['role-tag', { admin: role.code === 'admin' }]">{{ role.name }}</span></h3>
          <p>{{ role.description }}</p>
          <div class="role-card-meta">拥有此角色的用户：{{ getRoleUserCount(role.id) }} 人</div>
        </div>
      </div>

      <div class="footer-notes">
        <span>角色是唯一的模块访问来源。用户可同时拥有多个角色，最终可见模块取角色权限并集。</span>
        <span>暂不设计模块内部按钮级权限，后续在模块内部页面单独处理。</span>
      </div>
    </section>

    <!-- 操作审计 -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>操作审计</h2>
          <p>记录管理员对用户账号的所有操作，包括创建、修改、重置和状态变更。</p>
        </div>
      </div>

      <div class="audit-table">
        <div class="audit-header">
          <div>时间</div>
          <div>审计内容</div>
          <div>追溯详情</div>
          <div>结果</div>
        </div>

        <div v-if="loading" class="loading-state">加载中...</div>
        
        <div v-else-if="auditLogs.length === 0" class="empty-state">
          暂无审计记录
        </div>
        
        <div v-else v-for="log in auditLogs" :key="log.id" class="audit-row">
          <div class="audit-time">
            <span class="audit-cell-label">时间</span>
            <span>{{ formatDate(log.created_at) }}</span>
          </div>
          <div class="audit-content">
            <span class="audit-cell-label">审计内容</span>
            <div class="audit-summary">{{ getAuditSummary(log) }}</div>
          </div>
          <div class="audit-trace">
            <span class="audit-cell-label">追溯详情</span>
            <div v-if="getAuditDetailRows(log).length" class="audit-detail-list">
              <span v-for="item in getAuditDetailRows(log)" :key="item" class="audit-detail-chip">
                {{ item }}
              </span>
            </div>
            <span v-else class="text-muted">无补充详情</span>
          </div>
          <div class="audit-result">
            <span class="audit-cell-label">结果</span>
            <span :class="['status-badge', log.result === 'success' || !log.result ? 'active' : 'disabled']">
              {{ getAuditResultLabel(log.result) }}
            </span>
          </div>
        </div>
      </div>

      <!-- 审计日志分页控件 -->
      <div v-if="auditTotalPages > 1" class="pagination">
        <button
          class="btn btn-ghost btn-sm"
          :disabled="auditPage <= 1"
          @click="goToAuditPage(auditPage - 1)"
        >
          上一页
        </button>
        <div class="page-info">
          第 {{ auditPage }} / {{ auditTotalPages }} 页，共 {{ auditTotal }} 条
        </div>
        <button
          class="btn btn-ghost btn-sm"
          :disabled="auditPage >= auditTotalPages"
          @click="goToAuditPage(auditPage + 1)"
        >
          下一页
        </button>
      </div>
    </section>

    <!-- 创建账号弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal">
        <h2 class="modal-title">创建新账号</h2>
        <p class="modal-desc">为新用户创建账号并分配角色。</p>

        <div class="form-group">
          <label class="form-label">用户名 *</label>
          <input
            v-model="newUser.username"
            type="text"
            class="form-input"
            placeholder="输入用户名"
          />
        </div>

        <div class="form-group">
          <label class="form-label">初始密码 *</label>
          <input
            v-model="newUser.password"
            type="password"
            class="form-input"
            placeholder="输入初始密码（至少8位）"
          />
        </div>

        <div class="form-group">
          <label class="form-label">显示名称</label>
          <input
            v-model="newUser.display_name"
            type="text"
            class="form-input"
            placeholder="输入显示名称"
          />
        </div>

        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="newUser.email"
            type="email"
            class="form-input"
            placeholder="输入邮箱地址"
          />
        </div>

        <div class="form-group">
          <label class="form-label">角色 *</label>
          <div class="role-checkboxes">
            <label v-for="role in roles" :key="role.id" class="checkbox-item">
              <input
                type="checkbox"
                :value="role.id"
                v-model="newUser.role_ids"
              />
              <span>{{ role.name }}</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-item">
            <input
              type="checkbox"
              v-model="newUser.must_change_password"
            />
            <span>首次登录强制修改密码</span>
          </label>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showCreateModal = false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="createUser">
            {{ saving ? "创建中..." : "创建账号" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑用户弹窗 -->
    <div v-if="showEditModal && selectedUser" class="modal-overlay">
      <div class="modal">
        <h2 class="modal-title">编辑用户</h2>
        <p class="modal-desc">修改 {{ selectedUser.username }} 的信息和角色。</p>

        <div class="form-group">
          <label class="form-label">显示名称</label>
          <input
            v-model="selectedUser.profile.display_name"
            type="text"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="selectedUser.profile.email"
            type="email"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">角色</label>
          <div class="role-checkboxes">
            <label v-for="role in roles" :key="role.id" class="checkbox-item">
              <input
                type="checkbox"
                :checked="selectedUser.roles?.some(r => r.id === role.id)"
                @change="toggleRole(role.id)"
              />
              <span>{{ role.name }}</span>
            </label>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showEditModal = false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="updateUser">
            {{ saving ? "保存中..." : "保存修改" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 重置密码弹窗 -->
    <div v-if="showResetPasswordModal && selectedUser" class="modal-overlay">
      <div class="modal">
        <h2 class="modal-title">重置密码</h2>
        <p class="modal-desc">为 {{ selectedUser.username }} 重置密码。</p>

        <div class="form-group">
          <label class="form-label">新密码</label>
          <input
            v-model="resetPasswordForm.new_password"
            type="password"
            class="form-input"
            placeholder="输入新密码（至少8位）"
          />
        </div>

        <div class="form-group">
          <label class="checkbox-item">
            <input
              type="checkbox"
              v-model="resetPasswordForm.must_change_password"
            />
            <span>下次登录强制修改密码</span>
          </label>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showResetPasswordModal = false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="resetPassword">
            {{ saving ? "重置中..." : "确认重置" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 账号页共享设计令牌：浅色内容画布 */
.account-page {
  --canvas: #eef2f6;
  --surface: #f7f9fb;
  --surface-soft: #f1f4f7;
  --line: #dbe2ea;
  --line-soft: #e7edf2;
  --ink: #17202c;
  --copy: #556173;
  --muted: #7a8594;
  --accent: #315f8f;
  --danger: #b54242;
  --danger-bg: rgba(181, 66, 66, 0.08);
  --warning: #8c6841;
  --warning-bg: rgba(140, 104, 65, 0.08);
  --success: #0f766e;
  --success-bg: rgba(15, 118, 110, 0.08);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;

  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  background: var(--canvas);
  color: var(--ink);
  line-height: 1.6;
}

/* Section styles */
.section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
}

.section-header p {
  font-size: 14px;
  color: var(--muted);
}

/* Page header */
.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.page-label {
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
}

.page-title {
  font-size: clamp(24px, 3vw, 32px);
  line-height: 1.2;
  color: var(--ink);
  margin-bottom: 12px;
}

.page-desc {
  color: var(--copy);
  font-size: 15px;
  line-height: 1.6;
}

/* Alert banner */
.alert-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-md);
  margin-bottom: 24px;
  font-size: 14px;
  line-height: 1.5;
}

.alert-success {
  background: var(--success-bg);
  border: 1px solid rgba(15, 118, 110, 0.2);
  color: var(--success);
}

.alert-error {
  background: var(--danger-bg);
  border: 1px solid rgba(181, 66, 66, 0.2);
  color: var(--danger);
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 700;
}

.alert-success .alert-icon {
  background: rgba(15, 118, 110, 0.15);
}

.alert-error .alert-icon {
  background: rgba(181, 66, 66, 0.15);
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-md);
  padding: 20px;
}

.stat-label {
  font-size: 12px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.2;
}

.stat-note {
  margin-top: 4px;
  font-size: 12px;
  color: var(--muted);
}

/* Search bar */
.search-bar {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: 10px 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--ink);
  background: var(--canvas);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
}

/* User table */
.user-table {
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.user-table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr 1fr 2fr;
  padding: 12px 16px;
  background: var(--surface-soft);
  border-bottom: 1px solid var(--line-soft);
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.user-row {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr 1fr 2fr;
  padding: 16px;
  border-bottom: 1px solid var(--line-soft);
  font-size: 14px;
  align-items: center;
}

.user-row:last-child {
  border-bottom: none;
}

.user-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-sm {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #4a7ab5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
  color: var(--ink);
}

.user-email {
  font-size: 12px;
  color: var(--muted);
}

.user-last-login {
  font-size: 13px;
  color: var(--muted);
  white-space: nowrap;
}

.user-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Status badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: var(--success-bg);
  color: var(--success);
}

.status-badge.warning {
  background: var(--warning-bg);
  color: var(--warning);
}

.status-badge.disabled {
  background: var(--danger-bg);
  color: var(--danger);
}

/* Role tags */
.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.role-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  background: rgba(49, 95, 143, 0.1);
  color: var(--accent);
  border-radius: 10px;
  font-size: 12px;
}

.role-tag.admin {
  background: rgba(49, 95, 143, 0.2);
  font-weight: 600;
}

/* Security notice */
.security-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 20px;
  padding: 16px;
  background: var(--warning-bg);
  border: 1px solid rgba(140, 104, 65, 0.2);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--warning);
}

.security-notice-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(140, 104, 65, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

/* Role cards */
.role-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.role-card {
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.role-card h3 {
  margin-bottom: 8px;
}

.role-card p {
  font-size: 13px;
  color: var(--copy);
  margin-bottom: 12px;
  line-height: 1.5;
}

.role-card-meta {
  font-size: 12px;
  color: var(--muted);
}

/* Footer notes */
.footer-notes {
  margin-top: 20px;
  padding: 16px;
  background: var(--surface-soft);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  color: var(--muted);
}

/* Audit table */
.audit-table {
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.audit-header {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  padding: 12px 16px;
  background: var(--surface-soft);
  border-bottom: 1px solid var(--line-soft);
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.audit-row {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  padding: 12px 16px;
  border-bottom: 1px solid var(--line-soft);
  font-size: 14px;
  align-items: start;
}

.audit-row:last-child {
  border-bottom: none;
}

.audit-summary {
  color: var(--ink);
  font-weight: 500;
  line-height: 1.6;
}

.audit-detail-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.audit-detail-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--surface-soft);
  color: var(--copy);
  font-size: 12px;
  line-height: 1.4;
}

.audit-cell-label {
  display: none;
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--muted);
}

/* Loading and empty states */
.loading-state, .empty-state {
  padding: 40px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding: 16px;
}

.page-info {
  font-size: 14px;
  color: var(--muted);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 20px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
  border: none;
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-sm {
  min-height: 32px;
  padding: 0 12px;
  font-size: 12px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent), #4a7ab5);
  color: white;
}

.btn-secondary {
  background: var(--surface);
  color: var(--ink);
  border: 1px solid var(--line);
}

.btn-ghost {
  background: none;
  color: var(--accent);
  border: 1px solid var(--line);
}

.btn-ghost:hover {
  background: var(--surface-soft);
}

.btn-secondary.btn-ghost {
  color: var(--ink);
}

.text-muted {
  color: var(--muted);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 32px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 8px;
}

.modal-desc {
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--ink);
  background: var(--canvas);
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
}

.role-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--ink);
}

.checkbox-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
  }
  
  .user-table-header {
    display: none;
  }
  
  .user-row {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    background: var(--surface);
    border: 1px solid var(--line-soft);
    border-radius: var(--radius-md);
    margin-bottom: 12px;
  }
  
  .user-name-cell {
    width: 100%;
  }
  
  .user-last-login {
    font-size: 13px;
    color: var(--muted);
  }
  
  .user-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .audit-header,
  .audit-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .audit-header {
    display: none;
  }

  .audit-row {
    padding: 16px;
  }

  .audit-cell-label {
    display: block;
    margin-bottom: 4px;
  }

  .audit-detail-list {
    gap: 6px;
  }
  
  .role-cards {
    grid-template-columns: 1fr;
  }
}
</style>
