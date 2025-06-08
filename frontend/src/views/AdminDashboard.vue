<!-- src/views/AdminDashboard.vue -->
<template>
  <div class="admin-root">
    <NavBar :isDark="isDark" @toggle-theme="toggleTheme" />
    <div class="admin-main">
      <AdminSidebar />
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import AdminSidebar from '@/components/AdminSidebar.vue'

const isDark = ref(false)

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
.admin-root {
  min-height: 100vh;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
}
.admin-main {
  display: flex;
  flex: 1;
  min-height: 0;
}
.admin-content {
  flex: 1;
  min-width: 0;
  padding: 36px 30px 32px 30px;
  background: var(--color-bg);
  min-height: 100vh;
  overflow-x: auto;
}
</style>
