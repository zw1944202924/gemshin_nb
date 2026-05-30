<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const { login, pending, token } = useAuth()

const form = reactive({
  username: "",
  password: ""
})
const errorMessage = ref("")

if (token.value) {
  await navigateTo("/dashboard")
}

const submit = async () => {
  errorMessage.value = ""

  try {
    await login(form)
    const target = typeof route.query.redirect === "string" ? route.query.redirect : "/dashboard"
    await router.push(target)
  } catch (error) {
    const detail =
      typeof error === "object" &&
      error !== null &&
      "data" in error &&
      typeof error.data === "object" &&
      error.data !== null &&
      "detail" in error.data
        ? String(error.data.detail)
        : ""

    errorMessage.value = detail || "登录失败，请稍后重试"
  }
}
</script>

<template>
  <main class="auth-shell">
    <section class="auth-card">
      <p class="eyebrow">Gemshin Auth</p>
      <h1>登录第一条端到端链路</h1>
      <p class="intro">
        使用 Django 账号登录，建立最小 token 登录态，并跳转到受保护页面。
      </p>

      <form class="form" @submit.prevent="submit">
        <label class="field">
          <span>用户名</span>
          <input v-model="form.username" type="text" autocomplete="username" placeholder="demo" />
        </label>

        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" autocomplete="current-password" placeholder="请输入密码" />
        </label>

        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

        <button class="submit" type="submit" :disabled="pending">
          {{ pending ? "登录中..." : "登录" }}
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
.auth-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top, rgba(196, 224, 255, 0.7), transparent 38%),
    linear-gradient(160deg, #f7f7f2, #e7eef7 58%, #d8e3f5);
}

.auth-card {
  width: min(100%, 460px);
  padding: 36px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(22, 32, 51, 0.1);
  box-shadow: 0 24px 80px rgba(22, 32, 51, 0.12);
  backdrop-filter: blur(18px);
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #4b6381;
}

h1 {
  margin: 0;
  font-size: clamp(30px, 6vw, 44px);
}

.intro {
  margin: 14px 0 0;
  color: #42536d;
  line-height: 1.7;
}

.form {
  display: grid;
  gap: 16px;
  margin-top: 28px;
}

.field {
  display: grid;
  gap: 8px;
  font-weight: 600;
  color: #243246;
}

.field input {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid #c9d6e8;
  background: #fdfefe;
  font: inherit;
}

.field input:focus {
  outline: 2px solid #7ca5d6;
  outline-offset: 2px;
}

.error {
  margin: 0;
  color: #b42318;
}

.submit {
  border: 0;
  border-radius: 999px;
  padding: 14px 18px;
  font: inherit;
  font-weight: 700;
  color: #f5f7fb;
  background: linear-gradient(135deg, #0f4c81, #162033);
  cursor: pointer;
}

.submit:disabled {
  opacity: 0.6;
  cursor: wait;
}
</style>
