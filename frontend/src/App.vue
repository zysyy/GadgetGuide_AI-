<template>
  <div id="app">
    <header class="app-header">
      <h1>GadgetGuide AI</h1>
      <nav class="app-nav">
        <!-- 已登录显示功能按钮 -->
        <router-link v-if="isLogin" to="/chat">智能问答</router-link>
        <router-link v-if="isLogin" to="/upload">文档管理</router-link>
        <!-- 未登录显示登录/注册按钮 -->
        <router-link v-if="!isLogin" to="/login">登录</router-link>
        <router-link v-if="!isLogin" to="/register">注册</router-link>
        <!-- 登录后显示退出按钮 -->
        <a v-if="isLogin" href="#" @click.prevent="handleLogout">退出登录</a>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} GadgetGuide AI. (Demonstration Purposes)</p>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router"
import { removeToken } from "@/utils/token"
import { useAuth } from "@/composables/useAuth"

const router = useRouter()
const { isLogin, syncLoginStatus } = useAuth() // 一定要解构 syncLoginStatus！

function handleLogout() {
  removeToken()
  syncLoginStatus()  // 关键！让 isLogin 立刻变 false
  router.push("/login")
}
</script>

<style>
/* ...（样式与之前保持一致，省略）... */
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  color: var(--color-text-primary);
}

.app-header {
  background-color: var(--color-primary-deep-blue);
  color: var(--color-text-light);
  padding: calc(var(--spacing-unit, 8px) * 2) calc(var(--spacing-unit, 8px) * 3);
  text-align: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  border-bottom: 3px solid var(--color-primary-light-blue);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.app-header h1 {
  margin: 0;
  font-size: 1.9em;
  font-weight: 600;
  margin-bottom: calc(var(--spacing-unit, 8px) * 0.5);
}

.app-nav {
  margin-top: calc(var(--spacing-unit, 8px));
}

.app-nav a {
  font-weight: 500;
  color: var(--color-text-light);
  margin: 0 calc(var(--spacing-unit, 8px) * 1.5);
  text-decoration: none;
  padding: calc(var(--spacing-unit, 8px) * 0.75) var(--spacing-unit, 8px);
  border-radius: var(--border-radius-small, 4px);
  transition: background-color var(--transition-short, 0.2s ease-in-out), color var(--transition-short, 0.2s ease-in-out);
}

.app-nav a:hover {
  background-color: color-mix(in srgb, var(--color-primary-light-blue, #5db3d5) 25%, transparent);
}

.app-nav a.router-link-exact-active {
  color: var(--color-accent-yellow, #f1c40e);
  font-weight: 700;
  pointer-events: none;
}

.app-main {
  flex-grow: 1;
  padding: calc(var(--spacing-unit, 8px) * 2.5);
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.app-footer {
  background-color: var(--color-primary-medium-blue);
  color: var(--color-accent-green);
  text-align: center;
  padding: calc(var(--spacing-unit, 8px) * 1.5);
  font-size: 0.85em;
  margin-top: auto;
  border-top: 1px solid var(--color-primary-light-blue);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
