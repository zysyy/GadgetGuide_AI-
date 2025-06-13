<template>
  <router-view />
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { watch } from 'vue'

// 获取当前路由
const route = useRoute()

// 监听路由 meta.title 并设置 document.title
watch(
  () => route.meta.title,
  (title) => {
    document.title = title ? `${title} - GadgetGuide AI` : 'GadgetGuide AI'
  },
  { immediate: true } // 初始加载也设置标题
)
</script>
