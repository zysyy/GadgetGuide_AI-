<template>
  <div class="login-bg">
    <NavBar :isDark="isDark" @toggle-theme="toggleTheme" />
    <div class="center-area">
      <div class="login-card">
        <h2 class="title">登录 GadgetGuide AI</h2>
        <form @submit.prevent="handleLogin">
          <div class="form-item">
            <input
              v-model="username"
              type="text"
              placeholder="用户名或邮箱"
              autocomplete="username"
              required
            />
          </div>
          <div class="form-item">
            <input
              v-model="password"
              type="password"
              placeholder="密码"
              autocomplete="current-password"
              required
            />
          </div>
          <div class="form-action">
            <button type="submit" :disabled="loading">
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </div>
          <div class="form-bottom">
            <router-link to="/register" class="register-link">没有账号？注册</router-link>
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
const password = ref('')
const isDark = ref(false)
const loading = ref(false)
const router = useRouter()

async function handleLogin() {
  if (!username.value || !password.value) return
  loading.value = true
  try {
    const res = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    if (!res.ok) {
      const err = await res.json()
      alert(err.detail || '登录失败')
      loading.value = false
      return
    }
    const data = await res.json()
    // 保存 token
    localStorage.setItem('token', data.access_token)
    // 跳转到聊天主页面
    router.push('/chat')
  } catch (e) {
    alert('网络错误，请检查后端服务是否启动')
  } finally {
    loading.value = false
  }
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
.login-bg {
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
.login-card {
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
  opacity: 0.7;
  cursor: not-allowed;
}
.form-action button:hover:enabled {
  background: #2057c8;
}
.form-bottom {
  margin-top: 8px;
  text-align: right;
  width: 100%;
}
.register-link {
  color: var(--color-link);
  text-decoration: underline;
  font-size: 0.97em;
  transition: color 0.2s;
}
.register-link:hover {
  color: #235bdf;
}
</style>
