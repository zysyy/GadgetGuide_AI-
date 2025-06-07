<template>
  <header class="navbar">
    <div class="navbar-left">
      <!-- <img src="@/logo.svg" alt="logo" class="logo" /> -->
      <span class="app-title">GadgetGuide AI</span>
    </div>
    <div class="navbar-right">
      <slot name="right" />
      <button class="theme-btn" @click="$emit('toggle-theme')">
        <span v-if="isDark">☀️ 浅色</span>
        <span v-else>🌙 深色</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
const props = defineProps<{ isDark: boolean }>()
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
.logo {
  height: 32px;
  margin-right: 10px;
}
.navbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
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
