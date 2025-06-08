<template>
  <header class="navbar">
    <div class="navbar-left">
      <span class="app-title">GadgetGuide AI</span>
    </div>
    <div class="navbar-right">
      <!-- 只有管理员显示“切换”按钮 -->
      <button
        v-if="isAdmin"
        class="nav-btn"
        @click="handleSwitch"
      >
        {{ switchBtnLabel }}
      </button>
      <slot name="right" />
      <button class="theme-btn" @click="$emit('toggle-theme')">
        <span v-if="isDark">☀️ 浅色</span>
        <span v-else>🌙 深色</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const props = defineProps<{ isDark: boolean }>()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// ------- 关键1：刷新后自动恢复登录状态（可选，推荐放在 App.vue） -------
onMounted(() => {
  // 从 localStorage 恢复
  const raw = localStorage.getItem('user')
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      userStore.setUser(parsed)
    } catch {}
  }
})
// 每次登录 setUser 后同步存 localStorage
userStore.$subscribe((_mutation, state) => {
  localStorage.setItem('user', JSON.stringify({
    id: state.id,
    username: state.username,
    is_admin: state.is_admin,
    token: state.token
  }))
})
// ------- 关键1 END -------

// 管理员判断
const isAdmin = computed(() => userStore.is_admin === true)

// 动态按钮文本
const switchBtnLabel = computed(() => {
  if (route.path.startsWith('/admin')) {
    return '进入聊天'
  }
  return '进入后台'
})

// 切换路由
function handleSwitch() {
  if (route.path.startsWith('/admin')) {
    router.push('/chat')
  } else {
    router.push('/admin')
  }
}
</script>

<style scoped>
.navbar {
  width: 100%;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-sidebar);
  color: var(--color-main);
  padding: 0 32px;
  box-sizing: border-box;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.3s, color 0.3s;
  z-index: 99;
}
.navbar-left {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 1.12em;
  gap: 12px;
}
.app-title {
  letter-spacing: 0.5px;
}
.navbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.nav-btn {
  background: none;
  border: none;
  color: var(--color-link);
  font-size: 15px;
  border-radius: 8px;
  padding: 4px 16px;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.nav-btn:hover {
  background: var(--color-bot);
  color: var(--color-main);
}
.theme-btn {
  background: none;
  border: none;
  color: var(--color-link);
  font-size: 15px;
  border-radius: 8px;
  padding: 4px 16px;
  cursor: pointer;
  transition: background 0.15s;
}
.theme-btn:hover {
  background: var(--color-bot);
}
</style>
