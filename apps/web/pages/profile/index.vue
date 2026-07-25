<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true
})

const { user, logout, authorizedFetch } = useAuth()
const router = useRouter()

const profile = ref({
  display_name: "",
  email: "",
  notify_account_security: true,
  notify_permission_change: true,
  notify_module_activity: true
})

const passwordForm = ref({
  old_password: "",
  new_password: "",
  confirm_password: ""
})

const loading = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const showPasswordModal = ref(false)
const message = ref({ type: "", text: "" })

const mustChangePassword = computed(() => user.value?.must_change_password ?? false)

onMounted(async () => {
  await fetchProfile()
  if (mustChangePassword.value) {
    showPasswordModal.value = true
  }
})

async function fetchProfile() {
  loading.value = true
  try {
    const data = await authorizedFetch("/accounts/profile/")
    profile.value = {
      display_name: data.profile?.display_name || "",
      email: data.profile?.email || "",
      notify_account_security: data.profile?.notify_account_security ?? true,
      notify_permission_change: data.profile?.notify_permission_change ?? true,
      notify_module_activity: data.profile?.notify_module_activity ?? true
    }
  } catch (error) {
    message.value = { type: "error", text: "加载资料失败" }
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  saving.value = true
  message.value = { type: "", text: "" }
  try {
    await authorizedFetch("/accounts/profile/", {
      method: "PATCH",
      body: { profile: profile.value }
    })
    message.value = { type: "success", text: "资料已保存" }
  } catch (error) {
    message.value = { type: "error", text: "保存失败" }
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    message.value = { type: "error", text: "两次密码不一致" }
    return
  }

  changingPassword.value = true
  message.value = { type: "", text: "" }
  try {
    await authorizedFetch("/accounts/change-password/", {
      method: "POST",
      body: {
        old_password: passwordForm.value.old_password,
        new_password: passwordForm.value.new_password
      }
    })
    message.value = { type: "success", text: "密码修改成功" }
    showPasswordModal.value = false
    passwordForm.value = { old_password: "", new_password: "", confirm_password: "" }
    
    if (user.value) {
      user.value.must_change_password = false
    }
  } catch (error: any) {
    const detail = error?.data?.detail || error?.data?.old_password?.[0] || "密码修改失败"
    message.value = { type: "error", text: detail }
  } finally {
    changingPassword.value = false
  }
}

async function handleLogout() {
  await logout()
  await navigateTo("/")
}
</script>

<template>
  <div class="profile-page">
    <div class="page-header">
      <p class="page-label">个人中心</p>
      <h1 class="page-title">管理你的账户</h1>
      <p class="page-desc">查看和编辑个人资料、修改密码、管理通知偏好。</p>
    </div>

    <div v-if="mustChangePassword" class="alert-banner alert-warning">
      <div class="alert-icon">!</div>
      <div class="alert-content">
        <strong>需要修改密码</strong>
        你的账号首次登录或密码已被重置，请修改密码后继续使用。
      </div>
    </div>

    <div v-if="message.text" :class="['alert-banner', `alert-${message.type}`]">
      <div class="alert-icon">{{ message.type === "success" ? "✓" : "!" }}</div>
      <div class="alert-content">{{ message.text }}</div>
    </div>

    <div class="content-grid">
      <div class="card">
        <h2 class="card-title">个人资料</h2>
        <p class="card-desc">管理你的基本信息</p>
        
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            type="text"
            class="form-input"
            :value="user?.username"
            disabled
          />
          <p class="form-hint">用户名是登录标识，不可修改</p>
        </div>

        <div class="form-group">
          <label class="form-label">显示名称</label>
          <input
            v-model="profile.display_name"
            type="text"
            class="form-input"
            placeholder="输入显示名称"
          />
        </div>

        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="profile.email"
            type="email"
            class="form-input"
            placeholder="输入邮箱地址"
          />
        </div>

        <div class="form-actions">
          <button
            class="btn btn-primary"
            :disabled="saving"
            @click="saveProfile"
          >
            {{ saving ? "保存中..." : "保存资料" }}
          </button>
        </div>
      </div>

      <div class="card">
        <h2 class="card-title">账号状态</h2>
        <p class="card-desc">查看你的账号信息</p>

        <div class="info-row">
          <span class="info-label">账号状态</span>
          <span class="info-value status-active">正常</span>
        </div>

        <div class="info-row">
          <span class="info-label">角色</span>
          <div class="info-value">
            <div v-if="user?.roles?.length" class="role-tags">
              <span v-for="role in user.roles" :key="role.id" class="role-tag">
                {{ role.name }}
              </span>
            </div>
            <span v-else class="text-muted">暂无角色</span>
          </div>
        </div>

        <div class="info-row">
          <span class="info-label">模块权限</span>
          <div class="info-value">
            <div v-if="user?.roles?.length" class="module-tags">
              <template v-for="role in user.roles" :key="role.id">
                <span v-for="mod in role.modules" :key="mod.code" class="module-tag">
                  {{ mod.name }}
                </span>
              </template>
            </div>
            <span v-else class="text-muted">暂无模块权限</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="card-title">修改密码</h2>
        <p class="card-desc">定期修改密码以保护账号安全</p>

        <div class="form-group">
          <label class="form-label">旧密码</label>
          <input
            v-model="passwordForm.old_password"
            type="password"
            class="form-input"
            placeholder="输入当前密码"
          />
        </div>

        <div class="form-group">
          <label class="form-label">新密码</label>
          <input
            v-model="passwordForm.new_password"
            type="password"
            class="form-input"
            placeholder="输入新密码（至少8位）"
          />
        </div>

        <div class="form-group">
          <label class="form-label">确认新密码</label>
          <input
            v-model="passwordForm.confirm_password"
            type="password"
            class="form-input"
            placeholder="再次输入新密码"
          />
        </div>

        <div class="form-actions">
          <button
            class="btn btn-primary"
            :disabled="changingPassword"
            @click="changePassword"
          >
            {{ changingPassword ? "修改中..." : "修改密码" }}
          </button>
        </div>
      </div>

      <div class="card">
        <h2 class="card-title">通知偏好</h2>
        <p class="card-desc">管理站内通知接收设置</p>

        <div class="toggle-group">
          <label class="toggle-item">
            <span class="toggle-label">账号与安全通知</span>
            <input
              v-model="profile.notify_account_security"
              type="checkbox"
              class="toggle-input"
            />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div class="toggle-group">
          <label class="toggle-item">
            <span class="toggle-label">权限变更通知</span>
            <input
              v-model="profile.notify_permission_change"
              type="checkbox"
              class="toggle-input"
            />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div class="toggle-group">
          <label class="toggle-item">
            <span class="toggle-label">模块动态通知</span>
            <input
              v-model="profile.notify_module_activity"
              type="checkbox"
              class="toggle-input"
            />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div class="form-actions">
          <button
            class="btn btn-primary"
            :disabled="saving"
            @click="saveProfile"
          >
            {{ saving ? "保存中..." : "保存偏好" }}
          </button>
        </div>
      </div>

      <div class="card card-danger">
        <h2 class="card-title">退出登录</h2>
        <p class="card-desc">退出当前账号</p>
        <div class="form-actions">
          <button class="btn btn-danger" @click="handleLogout">
            退出登录
          </button>
        </div>
      </div>
    </div>

    <div v-if="showPasswordModal" class="modal-overlay">
      <div class="modal">
        <h2 class="modal-title">修改密码</h2>
        <p class="modal-desc">你的账号需要修改密码后才能继续使用。</p>

        <div class="form-group">
          <label class="form-label">旧密码</label>
          <input
            v-model="passwordForm.old_password"
            type="password"
            class="form-input"
            placeholder="输入当前密码"
          />
        </div>

        <div class="form-group">
          <label class="form-label">新密码</label>
          <input
            v-model="passwordForm.new_password"
            type="password"
            class="form-input"
            placeholder="输入新密码（至少8位）"
          />
        </div>

        <div class="form-group">
          <label class="form-label">确认新密码</label>
          <input
            v-model="passwordForm.confirm_password"
            type="password"
            class="form-input"
            placeholder="再次输入新密码"
          />
        </div>

        <div class="modal-actions">
          <button
            class="btn btn-primary"
            :disabled="changingPassword"
            @click="changePassword"
          >
            {{ changingPassword ? "修改中..." : "确认修改" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  margin-bottom: 32px;
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

.alert-warning {
  background: var(--warning-bg);
  border: 1px solid rgba(140, 104, 65, 0.2);
  color: var(--warning);
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

.alert-warning .alert-icon {
  background: rgba(140, 104, 65, 0.15);
}

.alert-success .alert-icon {
  background: rgba(15, 118, 110, 0.15);
}

.alert-error .alert-icon {
  background: rgba(181, 66, 66, 0.15);
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.card-danger {
  border-color: rgba(181, 66, 66, 0.2);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 8px;
}

.card-desc {
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 20px;
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

.form-input:disabled {
  background: var(--surface-soft);
  color: var(--muted);
}

.form-hint {
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
}

.form-actions {
  margin-top: 20px;
}

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

.btn-primary {
  background: linear-gradient(135deg, var(--accent), #4a7ab5);
  color: white;
}

.btn-danger {
  background: var(--danger);
  color: white;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid var(--line-soft);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: var(--muted);
  flex-shrink: 0;
  margin-right: 16px;
}

.info-value {
  font-size: 14px;
  color: var(--ink);
  text-align: right;
}

.status-active {
  color: var(--success);
  font-weight: 500;
}

.role-tags, .module-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}

.role-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: rgba(49, 95, 143, 0.1);
  color: var(--accent);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.module-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: var(--surface-soft);
  color: var(--copy);
  border-radius: 12px;
  font-size: 12px;
}

.text-muted {
  color: var(--muted);
}

.toggle-group {
  margin-bottom: 12px;
}

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.toggle-label {
  font-size: 14px;
  color: var(--ink);
}

.toggle-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--line);
  border-radius: 12px;
  transition: background 0.2s;
}

.toggle-slider::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-input:checked + .toggle-slider {
  background: var(--accent);
}

.toggle-input:checked + .toggle-slider::after {
  transform: translateX(20px);
}

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
  max-width: 400px;
  width: 90%;
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

.modal-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .info-row {
    flex-direction: column;
    gap: 4px;
  }
  
  .info-value {
    text-align: left;
  }
  
  .role-tags, .module-tags {
    justify-content: flex-start;
  }
}
</style>
