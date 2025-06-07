<!-- src/views/ChatPage.vue -->
<template>
  <div class="chat-page">
    <!-- 主导航栏 -->
    <NavBar :isDark="isDark" @toggle-theme="toggleTheme" />
    <div class="chat-body">
      <!-- 侧边栏 -->
      <Sidebar
        class="sidebar"
        :conversations="conversations"
        v-model:currentIndex="currentIndex"
        @new-conversation="addConversation"
        @delete-conversation="deleteConversation"
        @rename="renameConversation"
      />
      <!-- 主聊天区 -->
      <main class="chat-main">
        <div class="chat-toolbar">
          <button class="clear-btn" @click="clearCurrentConversation" :disabled="!currentConversation">
            清空消息
          </button>
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
          <div v-if="isThinking" class="bubble bot thinking">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
            <span style="margin-left:6px;">AI正在输入…</span>
          </div>
        </section>
        <footer class="chat-input">
          <input
            v-model="input"
            placeholder="请输入内容..."
            :disabled="isThinking || !currentConversation"
            @keyup.enter="send"
          />
          <button @click="send" :disabled="isThinking || !currentConversation">发送</button>
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

// --- 类型定义 ---
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

const router = useRouter()
const isDark = ref(false)
const conversations = ref<Conversation[]>([])
const currentIndex = ref(0)
const messages = ref<Message[]>([])
const input = ref('')
const chatContentEl = ref<HTMLElement | null>(null)
const isThinking = ref(false)
const token = localStorage.getItem("token") // 注意这里和你的login.vue/token名字统一！

const currentConversation = computed(() =>
  conversations.value.length > 0 ? conversations.value[currentIndex.value] : null
)

// ===== 主题切换 =====
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

// ===== 联动 API =====
// 1. 加载所有会话
async function fetchConversations() {
  const res = await fetch(`${API_BASE}/chat/conversations/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.status === 401) {
    router.push("/login"); return
  }
  conversations.value = await res.json()
  if (conversations.value.length > 0) {
    currentIndex.value = 0
    fetchMessages(conversations.value[0].id)
  } else {
    messages.value = []
  }
}

// 2. 加载会话消息
async function fetchMessages(conversationId: number) {
  messages.value = []
  isThinking.value = false
  const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}/messages/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.status === 401) { router.push("/login"); return }
  messages.value = await res.json()
  scrollToBottom()
}

// 3. 切换会话
watch(currentIndex, () => {
  const conv = conversations.value[currentIndex.value]
  if (conv) fetchMessages(conv.id)
})

// 4. 新建会话
async function addConversation() {
  const res = await fetch(`${API_BASE}/chat/conversations/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ title: `未命名会话 ${conversations.value.length + 1}` })
  })
  if (res.status === 401) { router.push("/login"); return }
  const conv = await res.json()
  conversations.value.unshift(conv)
  currentIndex.value = 0
  await fetchMessages(conv.id)
}

// 5. 删除会话（后端未实现物理删除接口，这里前端本地删）
async function deleteConversation(idx: number) {
  if (conversations.value.length <= 1) return
  conversations.value.splice(idx, 1)
  if (currentIndex.value >= conversations.value.length) currentIndex.value = conversations.value.length - 1
  const conv = conversations.value[currentIndex.value]
  if (conv) fetchMessages(conv.id)
  else messages.value = []
}

// 6. 重命名会话（可选：需后端 PATCH 支持，这里仅本地同步）
function renameConversation(idx: number, name: string) {
  if (!name.trim()) return
  conversations.value[idx].title = name.trim()
}

// 7. 发送消息并AI回复
async function send() {
  const text = input.value.trim()
  if (!text || !currentConversation.value) return
  isThinking.value = true

  // 1. 发送用户消息
  await fetch(`${API_BASE}/chat/conversations/${currentConversation.value.id}/messages/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ role: "user", content: text })
  })

  // 2. 让AI回复（你可以根据业务自己决定用哪个API，比如直接调用 /ask，然后保存进消息表）
  // 这里仅模拟等待2秒/可改为真实API
  await new Promise(r => setTimeout(r, 500))
  // 或者调用 /ask 并入库
  // const askRes = await fetch(`${API_BASE}/ask`, {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/x-www-form-urlencoded",
  //     Authorization: `Bearer ${token}`
  //   },
  //   body: new URLSearchParams({ query: text })
  // })
  // const askJson = await askRes.json()
  // await fetch(`${API_BASE}/chat/conversations/${currentConversation.value.id}/messages/`, {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/json",
  //     Authorization: `Bearer ${token}`
  //   },
  //   body: JSON.stringify({ role: "bot", content: askJson.answer })
  // })

  await fetchMessages(currentConversation.value.id)
  isThinking.value = false
  input.value = ""
}

function clearCurrentConversation() {
  // 这里只是本地清空，不会删除后端消息（你可以拓展后端清空接口）
  messages.value = []
}

// --- Markdown 渲染 ---
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
/* ... 你的样式完全保留 ... */
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-bg);
  color: var(--color-main);
}
.chat-body {
  display: flex;
  flex: 1;
  height: calc(100vh - 56px); /* NavBar高度 */
}
.sidebar {
  width: 240px;
  min-width: 200px;
  max-width: 280px;
  background: var(--color-sidebar);
  border-right: 1px solid var(--color-border);
  box-sizing: border-box;
  height: 100%;
}
.chat-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--color-bg);
}
.chat-toolbar {
  width: 100%;
  max-width: 700px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  padding: 12px 0 0 0;
}
.clear-btn {
  font-size: 13px;
  background: var(--color-bot);
  color: var(--color-link);
  border: none;
  border-radius: 6px;
  padding: 4px 14px;
  cursor: pointer;
  transition: background 0.15s;
}
.clear-btn:hover {
  background: var(--color-bot);
  filter: brightness(0.93);
}
.chat-content {
  flex: 1;
  width: 100%;
  max-width: 700px;
  min-width: 350px;
  margin: 0 auto;
  overflow-y: auto;
  padding: 32px 0;
  display: flex;
  flex-direction: column;
}
.bubble {
  max-width: 70%;
  min-width: 80px;
  padding: 16px 22px;
  margin: 10px 0;
  border-radius: 18px;
  word-break: break-all;
  display: flex;
  align-items: center;
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
.markdown :deep(p),
.markdown :deep(ul),
.markdown :deep(ol) {
  margin: 0 0 0.6em 0;
}
.markdown :deep(code) {
  background: var(--color-markdown-code-bg, #f4f4f4);
  border-radius: 4px;
  padding: 1px 4px;
  font-size: 0.98em;
  color: var(--color-markdown-code, #222);
}
.dark .markdown :deep(code) {
  background: var(--color-markdown-code-bg-dark, #232730);
  color: var(--color-markdown-code-dark, #ececec);
}
.markdown :deep(pre) {
  background: var(--color-markdown-pre-bg, #2b303b);
  color: var(--color-markdown-pre, #eaeaea);
  border-radius: 5px;
  padding: 12px;
  margin: 7px 0;
  overflow-x: auto;
}
.markdown :deep(a) {
  color: var(--color-link);
  text-decoration: underline;
}
.thinking {
  opacity: 0.8;
}
.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 3px;
  background: #b5c6e6;
  border-radius: 50%;
  animation: blink 1.4s infinite both;
}
.dot:nth-child(1) { animation-delay: 0s;}
.dot:nth-child(2) { animation-delay: 0.2s;}
.dot:nth-child(3) { animation-delay: 0.4s;}
@keyframes blink {
  0%, 80%, 100% { opacity: .4; }
  40% { opacity: 1; }
}
.chat-input {
  width: 100%;
  max-width: 700px;
  margin: 0 auto 16px auto;
  display: flex;
  padding: 18px 0 0 0;
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
}
.chat-input input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px 14px;
  margin-right: 12px;
  font-size: 16px;
  background: var(--color-sidebar);
  color: var(--color-main);
  transition: background 0.2s, color 0.2s;
}
.chat-input button {
  background: var(--color-user);
  color: var(--color-user-text);
  border: none;
  border-radius: 8px;
  padding: 0 28px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}
.chat-input input:disabled,
.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
