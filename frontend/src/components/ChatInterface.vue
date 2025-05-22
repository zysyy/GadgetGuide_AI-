<!-- src/components/ChatInterface.vue -->
<script setup>
import { ref, nextTick, watch } from 'vue'
import axios from '@/utils/axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  conversationId: Number
})

const userInput = ref('')
const messages = ref([])
const isLoading = ref(false)
const chatBox = ref(null)
const inputField = ref(null)
const isComposing = ref(false)
const enterKeyAfterComposition = ref(false)

watch(
  () => props.conversationId,
  async (id) => {
    messages.value = []
    userInput.value = ''
    if (!id) return
    try {
      const res = await axios.get(`/chat/conversations/${id}/messages/`)
      messages.value = res.data.map(msg => ({
        ...msg,
        role: msg.role || (msg.sender === 'bot' ? 'assistant' : 'user'),
        content: msg.content || msg.text
      }))
      if (messages.value.length === 0) {
        messages.value.push({
          role: 'assistant',
          content: '您好！我是 GadgetGuide AI，请问有什么电子产品的问题可以帮助您？',
          isError: false,
          tempKey: 'welcome'
        })
      }
      await nextTick()
      scrollToBottom()
    } catch (e) {
      messages.value.push({
        role: 'assistant',
        content: '无法加载历史消息，请刷新页面。',
        isError: true,
        tempKey: 'error-load'
      })
    }
  },
  { immediate: true }
)

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight
    }
  })
}

const renderMarkdown = (markdownText) => {
  if (typeof markdownText !== 'string') {
    return ''
  }
  const rawHtml = marked.parse(markdownText, { breaks: true, gfm: true })
  return DOMPurify.sanitize(rawHtml, { USE_PROFILES: { html: true } })
}

const handleCompositionStart = () => {
  isComposing.value = true
  enterKeyAfterComposition.value = false
}
const handleCompositionEnd = () => {
  isComposing.value = false
  if (userInput.value.trim() !== '') {
    enterKeyAfterComposition.value = true
  }
}
const handleEnterKey = () => {
  if (isComposing.value) return
  if (enterKeyAfterComposition.value) {
    enterKeyAfterComposition.value = false
    return
  }
  sendMessage()
}

const sendMessage = async () => {
  const query = userInput.value.trim()
  if (!query || isLoading.value || !props.conversationId) return

  isLoading.value = true
  const tempKey = 'temp-' + Date.now()
  messages.value.push({ role: 'user', content: query, isError: false, tempKey })
  userInput.value = ''
  enterKeyAfterComposition.value = false
  scrollToBottom()

  try {
    const res = await axios.post(`/chat/conversations/${props.conversationId}/messages/`, {
      role: 'user',
      content: query
    })
    messages.value = messages.value.filter(m => m.tempKey !== tempKey)
    messages.value.push(res.data)
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '发送失败：' + (error?.response?.data?.detail || error.message),
      isError: true,
      tempKey: 'send-error-' + Date.now()
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <div class="chat-container">
    <div class="chat-box" ref="chatBox">
      <div
        v-for="message in messages"
        :key="message.id || message.tempKey"
        :class="[
          'message-wrapper',
          message.role === 'user' ? 'user-message-wrapper' : 'bot-message-wrapper',
          message.isError ? 'error-message-wrapper' : ''
        ]"
      >
        <div class="avatar">
          {{ message.role === 'user' ? '您' : 'AI' }}
        </div>
        <div :class="['message-bubble', message.role === 'user' ? 'user-message' : 'bot-message', message.isError ? 'error-message' : '']">
          <div class="sender-name">{{ message.role === 'user' ? '' : 'GadgetGuide AI' }}</div>
          <div v-if="message.role === 'assistant' || message.role === 'bot'" class="markdown-content" v-html="renderMarkdown(message.content)"></div>
          <p v-else class="user-text-content">{{ message.content }}</p>
        </div>
      </div>
    </div>
    <div class="input-area">
      <input
        v-model="userInput"
        @keyup.enter="handleEnterKey"
        @compositionstart="handleCompositionStart"
        @compositionend="handleCompositionEnd"
        placeholder="请输入您的问题..."
        type="text"
        :disabled="isLoading || !conversationId"
        ref="inputField"
      />
      <button @click="sendMessage" :disabled="isLoading || !conversationId" class="send-button">
        <span v-if="isLoading">发送中...</span>
        <span v-else>发送</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  flex: 1 1 0%;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
  background: #fff;
  border-left: 1px solid #eee;
  z-index: 1;
  /* 不用 margin */
}

.chat-box {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 32px 0 12px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--color-background-page, #f0f2f5);
}

.message-wrapper {
  display: flex;
  align-items: flex-end;
  max-width: 75%;
  margin: 0 0 0 12px;
  /* 聊天气泡靠左，用户消息靠右 */
}

.user-message-wrapper {
  margin-left: auto;
  flex-direction: row-reverse;
  margin-right: 16px;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--color-primary-light-blue, #5db3d5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 12px;
  font-weight: 700;
  font-size: 1em;
}

.bot-message-wrapper .avatar {
  background: var(--color-accent-green, #a1d69f);
  color: var(--color-primary-deep-blue, #1f3a5b);
}

.message-bubble {
  padding: 14px 22px;
  border-radius: 20px;
  word-break: break-word;
  box-shadow: 0 1px 2px rgba(0,0,0,0.07);
  line-height: 1.6;
  background: #fff;
}

.user-message {
  background: var(--color-primary-medium-blue, #3b6c91);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bot-message {
  background: #f4f7fd;
  color: #212529;
  border-bottom-left-radius: 4px;
}

.error-message {
  background: #ffeeb6 !important;
  color: #856404 !important;
  border: 1px solid #ffeeba;
}

.sender-name {
  font-weight: 700;
  margin-bottom: 6px;
  font-size: 0.9em;
  color: #888;
}
.user-message .sender-name {
  display: none;
}

/* 输入区 */
.input-area {
  display: flex;
  align-items: center;
  padding: 18px 32px;
  border-top: 1px solid #eee;
  background: #fff;
}

.input-area input {
  flex: 1 1 0%;
  padding: 14px 22px;
  border: 1px solid #ced4da;
  border-radius: 25px;
  margin-right: 14px;
  font-size: 1em;
  outline: none;
  transition: border-color .2s, box-shadow .2s;
}
.input-area input:focus {
  border-color: #5db3d5;
  box-shadow: 0 0 0 0.1rem rgba(0,123,255,.10);
}
.send-button {
  padding: 12px 30px;
  background: #3b6c91;
  color: #fff;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 500;
  transition: background .2s;
}
.send-button:hover:not(:disabled) {
  background: #1f3a5b;
}
.send-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

@media (max-width: 800px) {
  .chat-box {
    padding: 6px 0 4px 0;
    gap: 8px;
  }
  .input-area {
    padding: 6px;
  }
  .avatar { width: 30px; height: 30px; }
  .message-wrapper, .user-message-wrapper { max-width: 95%; }
}

</style>
