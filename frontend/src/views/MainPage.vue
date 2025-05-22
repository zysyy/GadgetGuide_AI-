<!-- src/views/MainPage.vue -->
<template>
  <div class="main-layout">
    <ChatSidebar v-model="currentConversationId" />
    <div class="chat-main-area">
      <ChatInterface :conversation-id="currentConversationId" />
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import ChatSidebar from "@/components/ChatSidebar.vue"
import ChatInterface from "@/components/ChatInterface.vue"
const currentConversationId = ref(null)
</script>

<style scoped>
.main-layout {
  display: flex;
  height: calc(100vh - 90px); /* header/footer */
  width: 100vw;
  min-width: 0;
  background: #f5f7fa;
  overflow: hidden;
}

.chat-main-area {
  flex: 1 1 0%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: stretch;
  /* 限定最大宽度，左右自适应留白 */
  padding: 0;
  background: transparent;
}

/* 控制 ChatInterface 的宽度最大不超过 900px，居中 */
.chat-main-area > * {
  width: 100%;
  max-width: 1000px;
  min-width: 320px;
  height: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
}

/* 小屏自适应 */
@media (max-width: 900px) {
  .chat-main-area > * {
    max-width: 100vw;
    min-width: 0;
  }
}
</style>
