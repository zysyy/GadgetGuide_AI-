<!-- src/views/ChatPage.vue -->
<template>
  <div class="chat-page">
    <NavBar :isDark="isDark" @toggle-theme="toggleTheme" />
    <div class="chat-body">
      <Sidebar
        class="sidebar"
        :conversations="conversations"
        v-model:currentIndex="currentIndex"
        @new-conversation="addConversation"
        @delete-conversation="deleteConversation"
        @rename="renameConversation"
      />
      <main class="chat-main">
        <div class="chat-toolbar">
          <button class="clear-btn" @click="clearCurrentConversation" :disabled="!currentConversation">清空消息</button>
        </div>
        <section class="chat-content" ref="chatContentEl">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['bubble', msg.role === 'user' ? 'user' : 'bot']"
          >
            <div
              v-if="msg.role === 'assistant' || msg.role === 'bot'"
              class="markdown"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <template v-else>
              {{ msg.content }}
            </template>
          </div>
        </section>
        <footer class="chat-input">
          <input
            v-model="input"
            placeholder="请输入内容..."
            :disabled="!currentConversation"
            @keyup.enter="send"
          />
          <button @click="send" :disabled="!currentConversation">发送</button>
        </footer>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import NavBar from '@/components/NavBar.vue'
import Sidebar from '@/components/Sidebar.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useRouter } from 'vue-router'

const API_BASE = "http://localhost:8000"
const token = localStorage.getItem("token")!

const router = useRouter()
const isDark = ref(false)
const conversations = ref<Conversation[]>([])
const currentIndex = ref(0)
const messages = ref<Message[]>([])
const input = ref('')
const chatContentEl = ref<HTMLElement | null>(null)

interface Conversation {
  id: number
  title: string
}
interface Message {
  id: number
  role: 'user' | 'assistant' | 'bot'
  content: string
  created_at?: string
}

const currentConversation = computed(() =>
  conversations.value.length > 0 ? conversations.value[currentIndex.value] : null
)

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
  if (!token) {
    router.push("/login")
    return
  }
  fetchConversations()
})

async function fetchConversations() {
  const res = await fetch(`${API_BASE}/chat/conversations/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.status === 401) { router.push("/login"); return }
  conversations.value = await res.json()
  if (conversations.value.length > 0) {
    currentIndex.value = 0
    fetchMessages(conversations.value[0].id)
  } else {
    messages.value = []
  }
}
async function fetchMessages(conversationId: number) {
  const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}/messages/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.status === 401) { router.push("/login"); return }
  messages.value = await res.json()
  scrollToBottom()
}
watch(currentIndex, () => {
  const conv = conversations.value[currentIndex.value]
  if (conv) fetchMessages(conv.id)
})

async function addConversation() {
  const res = await fetch(`${API_BASE}/chat/conversations/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ title: `未命名会话` })
  })
  if (res.status === 401) { router.push("/login"); return }
  const conv = await res.json()
  conversations.value.unshift(conv)
  currentIndex.value = 0
  await fetchMessages(conv.id)
}

async function deleteConversation(idx: number) {
  const convId = conversations.value[idx].id
  await fetch(`${API_BASE}/chat/conversations/${convId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  })
  await fetchConversations()
}

async function renameConversation(idx: number, newTitle: string) {
  const convId = conversations.value[idx].id
  await fetch(`${API_BASE}/chat/conversations/${convId}/rename`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ title: newTitle })
  })
  await fetchConversations()
}

async function send() {
  const text = input.value.trim()
  if (!text || !currentConversation.value) return

  // 立即显示用户消息气泡
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: text
  })
  scrollToBottom()

  // 显示AI过渡气泡
  const thinkingBubbleId = Date.now() + 1
  messages.value.push({
    id: thinkingBubbleId,
    role: 'bot',
    content: 'AI正在输入…'
  })
  scrollToBottom()

  input.value = ""

  // 发送到后端
  await fetch(`${API_BASE}/chat/conversations/${currentConversation.value.id}/messages/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ role: "user", content: text })
  })

  // 拉取最新消息，替换掉AI过渡气泡
  await fetchMessages(currentConversation.value.id)
}

function clearCurrentConversation() {
  messages.value = []
}

function renderMarkdown(text: string) {
  const raw = marked.parse(text ?? '', { breaks: true, gfm: true })
  return DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } })
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContentEl.value) {
      chatContentEl.value.scrollTop = chatContentEl.value.scrollHeight
    }
  })
}
</script>

<style>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background: var(--color-bg);
  color: var(--color-main);
  overflow: hidden;
}

.chat-body {
  display: flex;
  flex: 1;
  height: calc(100vh - 56px);
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: var(--color-sidebar);
  border-right: 1px solid var(--color-border);
  box-sizing: border-box;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  overflow: hidden;
}

.chat-toolbar {
  display: flex;
  justify-content: flex-end;
  padding: 10px 16px 0;
}

.clear-btn {
  font-size: 13px;
  background: var(--color-bot);
  color: var(--color-link);
  border: none;
  border-radius: 6px;
  padding: 4px 14px;
  cursor: pointer;
}

.chat-content {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 32px 16px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.bubble {
  max-width: 85%;
  word-break: break-word;
  padding: 14px 18px;
  margin: 6px 0;
  border-radius: 16px;
  display: flex;
  font-size: 15px;
  line-height: 1.5;
}

.bot {
  background: var(--color-bot);
  color: var(--color-main);
  align-self: flex-start;
}

.user {
  background: var(--color-user);
  color: var(--color-user-text);
  align-self: flex-end;
}

.chat-input {
  width: 100%;
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  box-sizing: border-box;
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
}

.chat-input input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 16px;
  background: var(--color-sidebar);
  color: var(--color-main);
}

.chat-input button {
  background: var(--color-user);
  color: var(--color-user-text);
  border: none;
  border-radius: 8px;
  padding: 0 28px;
  font-size: 16px;
  cursor: pointer;
}

.chat-input input:disabled,
.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ========== 微调侧边栏内按钮间距与删除按钮居中 ========== */
.edit-btn {
  margin-left: 4px; /* 缩小和删除按钮的间距 */
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.edit-btn:hover {
  opacity: 1;
}

.delete-btn {
  background: #ff5959;
  border: none;
  color: #fff;
  font-size: 16px;
  margin-left: 4px; /* 原本8px改为4px，更紧凑 */
  cursor: pointer;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1; /* 保证×居中 */
  transition: background 0.2s, transform 0.2s;
}
.delete-btn:hover {
  background: #e04545;
  transform: scale(1.05);
}
</style>
