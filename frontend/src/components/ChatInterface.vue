<template>
  <div class="chat-container">
    <div class="chat-box" ref="chatBox">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="[
          'message-wrapper',
          message.sender === 'user' ? 'user-message-wrapper' : 'bot-message-wrapper',
          message.isError ? 'error-message-wrapper' : ''
        ]"
      >
        <div class="avatar">
          {{ message.sender === 'user' ? '您' : 'AI' }}
        </div>
        <div :class="['message-bubble', message.sender === 'user' ? 'user-message' : 'bot-message', message.isError ? 'error-message' : '']">
          <div class="sender-name">{{ message.sender === 'user' ? '' : 'GadgetGuide AI' }}</div>
          <div v-if="message.sender === 'bot'" class="markdown-content" v-html="renderMarkdown(message.text)"></div>
          <p v-else class="user-text-content">{{ message.text }}</p>
        </div>
      </div>
    </div>
    <div class="input-area">
      <input
        v-model="userInput"
        @keyup.enter="handleEnterKey"
        @compositionstart="handleCompositionStart" @compositionend="handleCompositionEnd"   placeholder="请输入您的问题..."
        type="text"
        :disabled="isLoading"
        ref="inputField"
      />
      <button @click="sendMessage" :disabled="isLoading" class="send-button">
        <span v-if="isLoading">发送中...</span>
        <span v-else>发送</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue';
import axios from 'axios';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// --- 响应式变量 ---
const userInput = ref('');
const messages = ref([]);
const isLoading = ref(false);
const chatBox = ref(null);
const inputField = ref(null);
const isComposing = ref(false);
const enterKeyAfterComposition = ref(false); // <--- 新增：用于更精确控制回车

// --- 配置 ---
const API_URL = 'http://127.0.0.1:8000/ask';

// --- 生命周期函数 ---
onMounted(() => {
  if (messages.value.length === 0) {
    messages.value.push({
      sender: 'bot',
      text: '您好！我是 GadgetGuide AI，请问有什么关于电子产品的问题我可以帮助您吗？',
      isError: false // 确保所有消息都有 isError 属性
    });
  }
  scrollToBottom();
  // inputField.value?.focus(); // 可选：初始聚焦
});

// --- 方法 ---
const scrollToBottom = () => {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight;
    }
  });
};

const renderMarkdown = (markdownText) => {
  if (typeof markdownText !== 'string') {
    return '';
  }
  const rawHtml = marked.parse(markdownText, { breaks: true, gfm: true });
  return DOMPurify.sanitize(rawHtml, { USE_PROFILES: { html: true } });
};

// --- 输入法和回车键处理逻辑 ---
const handleCompositionStart = () => {
  isComposing.value = true;
  enterKeyAfterComposition.value = false; // 在新的组合开始时，重置此标志
};

const handleCompositionEnd = () => {
  isComposing.value = false;
  // 当输入法组合（选词）结束后，如果输入框有内容，
  // 我们标记一下，表示下一次回车可能是选词的那个回车。
  if (userInput.value.trim() !== '') {
      enterKeyAfterComposition.value = true;
  }
};

const handleEnterKey = () => {
  if (isComposing.value) {
    // 如果仍在输入法组合中，这个回车是输入法内部的，不发送。
    return;
  }

  if (enterKeyAfterComposition.value) {
    // 如果这个回车紧跟在输入法组合结束之后，
    // 我们“消费”掉这次回车（即，不发送消息），并重置标志位。
    // 这样用户就需要再按一次回车才能真正发送。
    enterKeyAfterComposition.value = false;
    return;
  }

  // 只有在非组合状态，并且不是紧跟组合结束后的第一次回车时，才发送消息。
  sendMessage();
};
// --- 输入法和回车键处理逻辑结束 ---

const sendMessage = async () => {
  const query = userInput.value.trim();
  if (!query || isLoading.value) return;

  isLoading.value = true;
  messages.value.push({ sender: 'user', text: query, isError: false });
  userInput.value = '';
  enterKeyAfterComposition.value = false; // 发送后也重置标志位
  scrollToBottom();

  const formData = new FormData();
  formData.append('query', query);

  try {
    const response = await axios.post(API_URL, formData);
    let botText = '抱歉，未能获取到有效的回答格式。';
    let responseIsError = false;

    if (response.data) {
      if (response.data.answer) {
        botText = response.data.answer;
      } else if (response.data.message) {
        botText = response.data.message;
      } else if (response.data.detail && typeof response.data.detail === 'string') {
        botText = `错误: ${response.data.detail}`;
        responseIsError = true;
      }
    }
    messages.value.push({ sender: 'bot', text: botText, isError: responseIsError });

  } catch (error) {
    console.error('API请求错误:', error);
    let errorMessage = '抱歉，与服务器通信时发生错误 (Network Error)。';
    if (error.response && error.response.data && error.response.data.detail) {
      if (typeof error.response.data.detail === 'string') {
        errorMessage = `后端错误: ${error.response.data.detail}`;
      } else if (Array.isArray(error.response.data.detail) && error.response.data.detail.length > 0 && error.response.data.detail[0].msg) {
        errorMessage = `输入验证错误: ${error.response.data.detail[0].msg}`;
      }
    } else if (error.message && error.message.toLowerCase().includes('network error')) {
      errorMessage = '网络连接错误，请检查后端服务是否已启动并正确配置CORS。';
    } else if (error.message) {
        errorMessage = `请求发生错误: ${error.message}`;
    }
    messages.value.push({ sender: 'bot', text: errorMessage, isError: true });
  } finally {
    isLoading.value = false;
    scrollToBottom();
    // nextTick(() => inputField.value?.focus()); // 可选：发送后重新聚焦
  }
};
</script>

<style scoped>
/* 您之前提供的、已经应用了新配色的 <style scoped> 内容可以原样保留在这里 */
/* 例如：*/
.chat-container {
  display: flex;
  flex-direction: column;
  height: 85vh; 
  max-width: 768px; 
  min-width: 360px;
  margin: 1vh auto; 
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: var(--border-radius-large, 12px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
  background-color: var(--color-background-container, #ffffff);
  overflow: hidden;
  transition: all var(--transition-medium, 0.3s ease-in-out); 
}

.chat-box {
  flex-grow: 1;
  padding: calc(var(--spacing-unit, 8px) * 2) calc(var(--spacing-unit, 8px) * 2.5);
  overflow-y: auto;
  background-color: var(--color-background-page, #f0f2f5);
  border-bottom: 1px solid var(--color-border, #e0e0e0);
  scroll-behavior: smooth; 
}

.message-wrapper {
  display: flex;
  align-items: flex-end; 
  margin-bottom: calc(var(--spacing-unit, 8px) * 2);
  max-width: 85%;
  opacity: 0; 
  transform: translateY(15px); 
  animation: fadeInSlideUp 0.4s var(--transition-medium, 0.3s ease-in-out) forwards; 
}

@keyframes fadeInSlideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.avatar {
  width: 40px;   
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1em; 
  margin-right: calc(var(--spacing-unit, 8px) * 1.25); 
  flex-shrink: 0;
  color: var(--color-text-light, white); 
}

.user-message-wrapper {
  margin-left: auto; 
  flex-direction: row-reverse; 
}
.user-message-wrapper .avatar {
  background-color: var(--color-primary-light-blue, #5db3d5);
  margin-left: calc(var(--spacing-unit, 8px) * 1.25); 
  margin-right: 0;
}

.bot-message-wrapper .avatar {
  background-color: var(--color-accent-green, #a1d69f);
  color: var(--color-primary-deep-blue, #1f3a5b); 
}

.message-bubble {
  padding: calc(var(--spacing-unit, 8px) * 1.25) calc(var(--spacing-unit, 8px) * 1.8);
  border-radius: var(--border-radius-chat-bubble, 20px);
  word-wrap: break-word;
  box-shadow: 0 1px 2px rgba(0,0,0,0.07);
  line-height: 1.5;
}

.sender-name { /* 对所有 sender-name 生效，用户消息的 sender-name 在具体类中隐藏 */
  font-weight: bold;
  margin-bottom: calc(var(--spacing-unit, 8px) * 0.5);
  font-size: 0.85em; 
  display: block; 
}

.user-message { 
  background-color: var(--color-primary-medium-blue, #3b6c91);
  color: var(--color-text-light, white);
  border-bottom-right-radius: var(--border-radius-small, 4px);
  border-top-left-radius: var(--border-radius-chat-bubble, 20px);
  border-top-right-radius: var(--border-radius-chat-bubble, 20px);
  border-bottom-left-radius: var(--border-radius-chat-bubble, 20px);
}
.user-message .sender-name { display: none; } 
.user-text-content { 
  margin: 0;
}


.bot-message { 
  background-color: var(--color-background-elevated, #f0f3f5); 
  color: var(--color-text-primary, #212529);
  border-bottom-left-radius: var(--border-radius-small, 4px); 
  border-top-left-radius: var(--border-radius-chat-bubble, 20px);
  border-top-right-radius: var(--border-radius-chat-bubble, 20px);
  border-bottom-right-radius: var(--border-radius-chat-bubble, 20px);
}
.bot-message .sender-name {
  color: var(--color-primary-medium-blue, #3b6c91);
}

.markdown-content {
  line-height: 1.6;
  white-space: pre-wrap;
}
.markdown-content :deep(p) {
  margin-top: 0;
  margin-bottom: calc(var(--spacing-unit, 8px) * 0.75);
}
.markdown-content :deep(p):last-child { margin-bottom: 0; }
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) { 
  margin-top: calc(var(--spacing-unit, 8px) * 1.5);
  margin-bottom: calc(var(--spacing-unit, 8px) * 0.75);
  line-height: 1.3;
  color: var(--color-primary-deep-blue, #1f3a5b);
  font-weight: 600;
}
.markdown-content :deep(h1) { font-size: 1.4em; }
.markdown-content :deep(h2) { font-size: 1.25em; }
.markdown-content :deep(h3) { font-size: 1.1em; }

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: calc(var(--spacing-unit, 8px) * 2.5);
  margin-bottom: calc(var(--spacing-unit, 8px) * 0.75);
}
.markdown-content :deep(li) {
  margin-bottom: calc(var(--spacing-unit, 8px) * 0.5);
}
.markdown-content :deep(a) {
  color: var(--color-text-accent, #5db3d5);
  text-decoration: none;
  font-weight: 500;
}
.markdown-content :deep(a:hover) { text-decoration: underline; }
.markdown-content :deep(pre) {
  background-color: #282c34; 
  color: #abb2bf;
  padding: var(--spacing-unit, 8px);
  border-radius: var(--border-radius-medium, 8px); 
  overflow-x: auto;
  font-family: var(--font-family-monospace, monospace);
  font-size: 0.9em;
  margin: var(--spacing-unit, 8px) 0;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
}
.markdown-content :deep(code):not(pre > code) { 
  background-color: color-mix(in srgb, var(--color-border, #e0e0e0) 40%, transparent);
  color: var(--color-primary-deep-blue, #1f3a5b);
  padding: 2px 6px;
  border-radius: var(--border-radius-small, 4px);
  font-family: var(--font-family-monospace, monospace);
  font-size: 0.9em;
}
.bot-message .markdown-content :deep(p:first-child) { margin-top: 0; }

.error-message.message-bubble { 
  background-color: color-mix(in srgb, var(--color-accent-yellow, #f1c40e) 20%, white) !important; 
  color: color-mix(in srgb, var(--color-accent-yellow, #f1c40e) 90%, black 40%) !important;
  border: 1px solid var(--color-accent-yellow, #f1c40e);
}
.error-message-wrapper .avatar { 
  background-color: var(--color-accent-yellow, #f1c40e);
  color: var(--color-text-primary, black);
}
.error-message .sender-name {
  color: color-mix(in srgb, var(--color-accent-yellow, #f1c40e) 90%, black 40%) !important;
}


.input-area {
  display: flex;
  align-items: center;
  padding: calc(var(--spacing-unit, 8px) * 1.5) calc(var(--spacing-unit, 8px) * 2);
  border-top: 1px solid var(--color-border, #e0e0e0);
  background-color: var(--color-background-container, #ffffff);
}

.input-area input {
  flex-grow: 1;
  padding: calc(var(--spacing-unit, 8px) * 1.5);
  border: 1px solid var(--color-border, #ced4da);
  border-radius: var(--border-radius-input, 25px);
  margin-right: var(--spacing-unit, 8px);
  font-size: 1em;
  outline: none;
  transition: border-color var(--transition-short, 0.2s ease-in-out), box-shadow var(--transition-short, 0.2s ease-in-out);
}
.input-area input:focus {
  border-color: var(--color-primary-light-blue, #5db3d5);
  box-shadow: 0 0 0 0.2rem var(--color-shadow-focus, rgba(0,123,255,.25));
}

.send-button { 
  padding: calc(var(--spacing-unit, 8px) * 1.5) calc(var(--spacing-unit, 8px) * 2.5);
  background-color: var(--color-primary-medium-blue, #3b6c91);
  color: var(--color-text-on-primary, white);
  border: none;
  border-radius: var(--border-radius-input, 25px);
  cursor: pointer;
  font-size: 1em;
  font-weight: 500; 
  transition: background-color var(--transition-short, 0.2s ease-in-out);
}

.send-button:hover:not(:disabled) {
  background-color: var(--color-primary-deep-blue, #1f3a5b);
}
.send-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 响应式设计示例 */
@media (max-width: 768px) {
  .chat-container {
    margin: 0;
    border-radius: 0;
    height: 100vh; 
    max-width: 100%;
    border: none;
    box-shadow: none;
  }
  .chat-box {
    padding: var(--spacing-unit, 8px);
  }
  .input-area {
    padding: var(--spacing-unit, 8px);
  }
  .input-area input, .send-button {
    font-size: 0.95em;
    padding: var(--spacing-unit, 8px) calc(var(--spacing-unit, 8px) * 1.5);
  }
  .message-wrapper {
    max-width: 90%; 
  }
  .avatar {
    width: 32px;
    height: 32px;
    font-size: 0.8em;
  }
}
</style>