<!-- src/components/ChatSidebar.vue -->
<template>
  <aside class="sidebar">
    <button class="new-conv-btn" @click="handleNewConversation">＋ 新建会话</button>
    <ul class="conversation-list">
      <li
        v-for="conv in conversations"
        :key="conv.id"
        :class="{ active: conv.id === modelValue }"
        @click="selectConversation(conv.id)"
      >
        <span class="conv-title">{{ conv.title || '未命名会话' }}</span>
        <span class="conv-time">{{ formatTime(conv.created_at) }}</span>
      </li>
    </ul>
  </aside>
</template>

<script setup>
// 组合式API，支持v-model
import { ref, onMounted, defineProps, defineEmits } from "vue"
import axios from "@/utils/axios"

// 只声明，不赋值变量
defineProps({
  modelValue: Number // 选中的会话id
})
const emits = defineEmits(["update:modelValue"])

const conversations = ref([])

// 拉取会话列表
const fetchConversations = async () => {
  try {
    const res = await axios.get("/chat/conversations/")
    conversations.value = res.data
  } catch (e) {
    conversations.value = []
  }
}

// 切换会话
const selectConversation = (id) => {
  emits("update:modelValue", id)
}

// 新建会话
const handleNewConversation = async () => {
  try {
    const res = await axios.post("/chat/conversations/", { title: "" })
    await fetchConversations()
    emits("update:modelValue", res.data.id)
  } catch (e) {
    // 可选：报错提示
  }
}

// 格式化时间
const formatTime = (t) => {
  return new Date(t).toLocaleString().slice(0, 16)
}

onMounted(fetchConversations)
</script>

<style scoped>
.sidebar {
  width: 230px;
  min-width: 180px;
  background: #f9fafb;
  border-right: 1px solid #e0e0e0;
  padding: 14px 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.new-conv-btn {
  margin: 0 12px 18px 12px;
  padding: 6px 0;
  width: calc(100% - 24px);
  border: none;
  border-radius: 6px;
  background: #2866e7;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
}
.conversation-list {
  flex: 1;
  list-style: none;
  margin: 0;
  padding: 0 8px;
  overflow-y: auto;
}
.conversation-list li {
  padding: 10px 10px 10px 16px;
  border-radius: 5px;
  margin-bottom: 4px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.conversation-list li.active,
.conversation-list li:hover {
  background: #e3eafc;
}
.conv-title {
  font-weight: 500;
}
.conv-time {
  font-size: 0.8em;
  color: #888;
  margin-left: 8px;
}
.sidebar {
  width: 230px;
  min-width: 180px;
  background: #f9fafb;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  height: 100%;
  z-index: 2;
}

</style>
