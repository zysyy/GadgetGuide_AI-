<!-- src/components/TypingBubble.vue -->
<template>
  <span class="typing-text">
    AI 正在输入中
    <span class="dot" v-for="n in 3" :key="n" :style="{ animationDelay: `${n * 0.2}s` }">.</span>
  </span>
</template>

<script setup lang="ts">
// 无逻辑，只负责展示动画
</script>

<style scoped>
.typing-text {
  display: inline-flex;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.dot {
  display: inline-block;
  margin-left: 2px;
  font-size: 20px;
  line-height: 1;
  animation: blink 1.4s infinite ease-in-out;
  transform-origin: center;
}

@keyframes blink {
  0%, 80%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1.2);
  }
}
</style>
