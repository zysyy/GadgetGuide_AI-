<template>
  <div class="chat-page">
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
        @update-conversations="updateConversations"
      />

      <!-- 主聊天区 -->
      <main class="chat-main">
        <div class="chat-toolbar">
          <button class="clear-btn" @click="clearCurrentConversation" :disabled="!currentConversation">
            清空消息
          </button>
        </div>
        <section class="chat-content" ref="chatContentEl">
          <!-- 聊天消息列表 -->
          <div
            v-for="(msg, i) in messages"
            :key="msg.id"
            :class="['message-item', msg.role === 'user' ? 'user' : 'bot']"
          >
            <!-- 头像部分 -->
            <div class="avatar">{{ msg.role === 'user' ? userAvatar : 'AI' }}</div>

            <!-- 消息气泡部分 -->
            <div class="bubble">
              <!-- 动态加载 AI 输入动画 -->
              <TypingBubble v-if="msg.role === 'bot' && msg.content === 'AI正在输入…'" />
              <div
                v-else-if="msg.role === 'assistant' || msg.role === 'bot'"
                class="markdown"
                v-html="renderMarkdown(msg.content)"
              ></div>
              <template v-else>
                {{ msg.content }}
              </template>
            </div>
          </div>
        </section>

        <!-- 输入栏 -->
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
import TypingBubble from '@/components/TypingBubble.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useRouter } from 'vue-router'

const API_BASE = "http://localhost:8000"
const token = localStorage.getItem("token")!
const username = localStorage.getItem("username") || "用户"

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

// 提取用户名第一个非空字符作为头像
const userAvatar = computed(() => {
  const clean = username.trim().replace(/\s/g, '')
  return clean ? clean.charAt(0).toUpperCase() : 'U'
})

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

// 获取所有会话
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

// 拉取消息记录
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

// 新增会话
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

// 删除会话
async function deleteConversation(idx: number) {
  const convId = conversations.value[idx].id
  await fetch(`${API_BASE}/chat/conversations/${convId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  })
  await fetchConversations()
}

// 重命名会话
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

function updateConversations(newConvs: Conversation[]) {
  conversations.value = newConvs
}

// 发送消息逻辑（含过渡气泡）
async function send() {
  const text = input.value.trim()
  if (!text || !currentConversation.value) return

  messages.value.push({ id: Date.now(), role: 'user', content: text })
  scrollToBottom()

  const thinkingBubbleId = Date.now() + 1
  messages.value.push({ id: thinkingBubbleId, role: 'bot', content: 'AI正在输入…' })
  scrollToBottom()

  input.value = ""

  await fetch(`${API_BASE}/chat/conversations/${currentConversation.value.id}/messages/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ role: "user", content: text })
  })

  await fetchMessages(currentConversation.value.id)
}

function clearCurrentConversation() {
  messages.value = []
}

function renderMarkdown(text: string) {
  const rawHtml = marked.parse(text ?? '', { breaks: true, gfm: true })
  const dom = new DOMParser().parseFromString(rawHtml, 'text/html')

  // 精确处理：只移除表格内的 •
  dom.querySelectorAll('table td').forEach(td => {
    td.innerHTML = td.innerHTML.replace(/•\s*/g, '')
  })

  return DOMPurify.sanitize(dom.body.innerHTML, { USE_PROFILES: { html: true } })
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
  padding: 16px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.message-item {
  display: flex;
  align-items: flex-start;
  margin: 10px 0;
  transition: all 0.2s ease;
}
.message-item.user {
  flex-direction: row-reverse;
}

.avatar {
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  background: var(--color-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  margin: 0 8px;
  color: white;
}

.bubble {
  max-width: 80%;
  padding: 10px 14px;
  word-break: break-word;
  line-height: 1.5;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  border-radius: 16px 16px 16px 4px;
}

.bot .bubble {
  background: var(--color-bot);
  color: var(--color-main);
  align-self: flex-start;
  border-top-left-radius: 4px;   /* 左上角更尖锐，气泡箭头起点 */
  border-top-right-radius: 16px;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
}
.user .bubble {
  background: var(--color-user);
  color: var(--color-user-text);
  border-radius: 16px 16px 4px 16px;
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

.markdown table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 15px;
  background-color: #f4f7fb; /* ✅ 设置一个与气泡不同的背景 */
  border-radius: 6px;
  overflow: hidden;
}

.markdown th,
.markdown td {
  border: 1px solid #d4d9e1;
  padding: 10px 12px;
  text-align: left;
  vertical-align: top;
  color: #333;
}

.markdown th {
  background-color: #eaf1fa; /* ✅ 表头颜色偏淡蓝 */
  font-weight: 600;
}

.markdown tr:nth-child(even) td {
  background-color: #fdfefe; /* ✅ 偶数行为白色，避免一片蓝 */
}

</style>