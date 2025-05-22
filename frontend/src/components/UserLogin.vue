<!-- src/components/UserLogin.vue -->
<template>
  <div class="login-container">
    <h2>登录</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required />
      <button type="submit">登录</button>
      <router-link to="/register">没有账号？立即注册</router-link>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { login } from "@/api/auth"
import { setToken } from "@/utils/token"
import { useRouter } from "vue-router"
import { useAuth } from "@/composables/useAuth" // 👈 导入

const router = useRouter()
const username = ref("")
const password = ref("")
const error = ref("")
const { syncLoginStatus } = useAuth() // 👈 解构

const handleLogin = async () => {
  try {
    const res = await login(username.value, password.value)
    setToken(res.data.access_token)
    syncLoginStatus()            // 👈 登录成功后同步
    router.push("/chat")
  } catch (err) {
    error.value = err?.response?.data?.detail || "登录失败"
  }
}
</script>

<style scoped>
.login-container {
  max-width: 300px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.login-container input {
  width: 100%;
  margin: 8px 0;
  padding: 8px;
}
.error {
  color: red;
  margin-top: 10px;
}
</style>
