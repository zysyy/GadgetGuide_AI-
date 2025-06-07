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
          <div class="form-action">
            <button type="submit">注册</button>
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
import NavBar from '@/components/NavBar.vue'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isDark = ref(false)

function handleRegister() {
  // TODO: 校验逻辑 & API 提交
  if (password.value !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }
  // ...实际注册逻辑
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
</style>
