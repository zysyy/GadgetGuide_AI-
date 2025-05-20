<!-- src/components/UserRegister.vue -->
<template>
    <div class="register-container">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <input v-model="username" placeholder="用户名" required />
        <input v-model="password" type="password" placeholder="密码" required />
        <input v-model="confirmPassword" type="password" placeholder="确认密码" required />
        <button type="submit">注册</button>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>
      </form>
      <router-link to="/login">已有账号？去登录</router-link>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue"
  import { register } from "@/api/auth"
  import { useRouter } from "vue-router"
  
  const router = useRouter()
  const username = ref("")
  const password = ref("")
  const confirmPassword = ref("")
  const error = ref("")
  const success = ref("")
  
  const handleRegister = async () => {
    error.value = ""
    success.value = ""
    if (password.value !== confirmPassword.value) {
      error.value = "两次输入密码不一致"
      return
    }
    try {
      await register(username.value, password.value)
      success.value = "注册成功，请登录"
      setTimeout(() => {
        router.push("/login")
      }, 1000)
    } catch (err) {
      error.value = err?.response?.data?.detail || "注册失败"
    }
  }
  </script>
  
  <style scoped>
  .register-container {
    max-width: 300px;
    margin: 100px auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 6px;
  }
  .register-container input {
    width: 100%;
    margin: 8px 0;
    padding: 8px;
  }
  .error {
    color: red;
    margin-top: 10px;
  }
  .success {
    color: green;
    margin-top: 10px;
  }
  </style>
  