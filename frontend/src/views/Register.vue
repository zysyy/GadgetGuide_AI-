<!-- src/views/Register.vue -->
<template>
  <div class="register-bg">
    <NavBar :isDark="isDark" @toggle-theme="toggleTheme" />
    <div class="center-area">
      <div class="register-card">
        <h2 class="title">注册 GadgetGuide AI</h2>
        <form @submit.prevent="handleRegister">
          <div class="form-item">
            <input
              v-model="username"
              type="text"
              placeholder="用户名"
              autocomplete="username"
              required
            />
          </div>
          <div class="form-item">
            <input
              v-model="email"
              type="email"
              placeholder="邮箱"
              autocomplete="email"
              required
            />
          </div>
          <div class="form-item">
            <input
              v-model="password"
              type="password"
              placeholder="密码"
              autocomplete="new-password"
              required
            />
          </div>
          <div class="form-item">
            <input
              v-model="confirmPassword"
              type="password"
              placeholder="确认密码"
              autocomplete="new-password"
              required
            />
          </div>
          <div v-if="errorMsg" class="error-tip">{{ errorMsg }}</div>
          <div v-if="successMsg" class="success-tip">{{ successMsg }}</div>
          <div class="form-action">
            <button type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? "注册中..." : "注册" }}
            </button>
          </div>
          <div class="form-bottom">
            <router-link to="/login" class="login-link">已有账号？去登录</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const isDark = ref(false)
const router = useRouter()

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    errorMsg.value = '请填写完整信息'
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  isSubmitting.value = true
  try {
    const res = await fetch('http://localhost:8000/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value,
      })
    })
    if (!res.ok) {
      const data = await res.json()
      errorMsg.value = data.detail || '注册失败'
    } else {
      successMsg.value = '注册成功，正在跳转登录页...'
      setTimeout(() => {
        router.push('/login')
      }, 1200)
    }
  } catch (e: any) {
    errorMsg.value = '网络异常，请重试'
  }
  isSubmitting.value = false
}

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}
onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})
</script>

<style scoped>
.register-bg {
  min-height: 100vh;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
  transition: background 0.3s;
}
.center-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.register-card {
  background: var(--color-sidebar);
  box-shadow: 0 4px 32px rgba(60,72,90,0.08), 0 1.5px 5px rgba(0,0,0,0.03);
  border-radius: 16px;
  padding: 36px 28px 28px 28px;
  width: 340px;
  max-width: 92vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: background 0.3s, box-shadow 0.3s;
}
.title {
  text-align: center;
  color: var(--color-main);
  font-size: 1.42em;
  font-weight: 700;
  margin-bottom: 32px;
  letter-spacing: 1px;
}
form {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.form-item {
  width: 100%;
  margin-bottom: 18px;
}
.form-item input {
  width: 100%;
  padding: 12px 14px;
  font-size: 1em;
  background: var(--color-bg);
  color: var(--color-main);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  outline: none;
  transition: background 0.2s, color 0.2s, border 0.2s;
  box-sizing: border-box;
}
.form-item input:focus {
  border: 1.5px solid var(--color-link);
}
.form-action {
  width: 100%;
  margin-top: 8px;
  margin-bottom: 10px;
}
.form-action button {
  width: 100%;
  padding: 12px 0;
  border-radius: 8px;
  background: var(--color-user);
  color: var(--color-user-text);
  font-size: 1.09em;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.18s;
  box-sizing: border-box;
}
.form-action button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.form-action button:hover {
  background: #2057c8;
}
.form-bottom {
  margin-top: 8px;
  text-align: right;
  width: 100%;
}
.login-link {
  color: var(--color-link);
  text-decoration: underline;
  font-size: 0.97em;
  transition: color 0.2s;
}
.login-link:hover {
  color: #235bdf;
}
.error-tip {
  width: 100%;
  color: #ff5454;
  background: #fff1f1;
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 6px;
  font-size: 0.98em;
  text-align: center;
}
.success-tip {
  width: 100%;
  color: #11bb80;
  background: #e7fff4;
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 6px;
  font-size: 0.98em;
  text-align: center;
}
</style>
