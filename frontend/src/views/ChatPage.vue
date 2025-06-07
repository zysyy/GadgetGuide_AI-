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
          <button class="clear-btn" @click="clearCurrentConversation">
            清空消息
          </button>
        </div>
        <section class="chat-content" ref="chatContentEl">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['bubble', msg.role]"
          >
            <div
              v-if="msg.role === 'bot'"
              class="markdown"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <template v-else>
              {{ msg.content }}
            </template>
          </div>
          <div
            v-if="isThinking"
            class="bubble bot thinking"
          >
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
            :disabled="isThinking"
            @keyup.enter="send"
          />
          <button @click="send" :disabled="isThinking">发送</button>
        </footer>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import Sidebar from '@/components/Sidebar.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

type Message = {
  role: 'user' | 'bot'
  content: string
}

const conversations = ref<string[]>([
  '未命名会话 1',
  '未命名会话 2',
  '未命名会话 3'
])
const allMessages = ref<Message[][]>([
  [
    { role: 'bot', content: '你好，有什么可以帮您？\n\n**支持Markdown格式！**\n\n- 试试：`代码`、列表、链接\n- [GadgetGuide AI](#)' },
    { role: 'user', content: '请问iPhone 15怎么样？' }
  ],
  [
    { role: 'bot', content: '欢迎来到会话2' }
  ],
  [
    { role: 'bot', content: '这是会话3' }
  ]
])
const currentIndex = ref(0)
const messages = computed(() => allMessages.value[currentIndex.value] || [])
const input = ref('')

const chatContentEl = ref<HTMLElement | null>(null)
const isThinking = ref(false)

// ===== 主题切换 =====
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

function scrollToBottom() {
  nextTick(() => {
    if (chatContentEl.value) {
      chatContentEl.value.scrollTop = chatContentEl.value.scrollHeight
    }
  })
}

function renderMarkdown(text: string) {
  const raw = marked.parse(text ?? '', { breaks: true, gfm: true })
  return DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } })
}

function send() {
  const text = input.value.trim()
  if (!text || isThinking.value) return
  allMessages.value[currentIndex.value].push({ role: 'user', content: text })
  input.value = ''
  scrollToBottom()
  isThinking.value = true

  setTimeout(() => {
    allMessages.value[currentIndex.value].push({
      role: 'bot',
      content: `AI：收到，你说「${text}」\n\n*（支持 Markdown 语法）*`
    })
    isThinking.value = false
    scrollToBottom()
  }, 2000)
}

function addConversation() {
  const newName = `未命名会话 ${conversations.value.length + 1}`
  conversations.value.push(newName)
  allMessages.value.push([
    { role: 'bot', content: '您好，新会话已创建，可以开始提问！' }
  ])
  currentIndex.value = conversations.value.length - 1
  nextTick(scrollToBottom)
}

function deleteConversation(i: number) {
  if (conversations.value.length <= 1) {
    return
  }
  conversations.value.splice(i, 1)
  allMessages.value.splice(i, 1)
  if (currentIndex.value === i) {
    currentIndex.value = Math.max(0, i - 1)
  } else if (currentIndex.value > i) {
    currentIndex.value--
  }
  nextTick(scrollToBottom)
}

function renameConversation(i: number, name: string) {
  if (name.trim()) {
    conversations.value[i] = name.trim()
  }
}

function clearCurrentConversation() {
  const i = currentIndex.value
  allMessages.value[i] = [
    { role: 'bot', content: '您好，消息已清空，可以重新开始！' }
  ]
  nextTick(scrollToBottom)
}
</script>

<style>
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
