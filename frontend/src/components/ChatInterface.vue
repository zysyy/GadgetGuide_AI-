<template>
    <div class="chat-container">
      <div class="chat-box" ref="chatBox">
        <div v-for="(message, index) in messages" :key="index"
             :class="['message-bubble', message.sender === 'user' ? 'user-message' : 'bot-message']">
          <p><strong>{{ message.sender === 'user' ? '您' : 'GadgetGuide AI' }}:</strong></p>
          <div v-if="message.sender === 'bot'" class="markdown-content" v-html="renderMarkdown(message.text)"></div>
          <p v-else>{{ message.text }}</p>
        </div>
      </div>
      <div class="input-area">
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          placeholder="请输入您的问题..."
          type="text"
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading">
          {{ isLoading ? '发送中...' : '发送' }}
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, nextTick } from 'vue';
  import axios from 'axios';
  import { marked } from 'marked';     // <--- 1. 导入 marked
  import DOMPurify from 'dompurify'; // <--- 2. 导入 DOMPurify
  
  // 响应式变量
  const userInput = ref('');
  const messages = ref([]);
  const isLoading = ref(false);
  const chatBox = ref(null);
  
  const API_URL = 'http://127.0.0.1:8000/ask';
  
  const scrollToBottom = () => {
    nextTick(() => {
      if (chatBox.value) {
        chatBox.value.scrollTop = chatBox.value.scrollHeight;
      }
    });
  };
  
  // 3. 创建一个方法来解析 Markdown 并净化 HTML
  const renderMarkdown = (markdownText) => {
    if (typeof markdownText !== 'string') {
      return ''; // 或者返回一些默认的错误提示文本
    }
    // 先用 marked 将 markdown 转为 HTML，然后用 DOMPurify 清理它
    const rawHtml = marked.parse(markdownText);
    return DOMPurify.sanitize(rawHtml);
  };
  
  const sendMessage = async () => {
    const query = userInput.value.trim();
    if (!query || isLoading.value) return;
  
    isLoading.value = true;
    messages.value.push({ sender: 'user', text: query });
    userInput.value = '';
    scrollToBottom();
  
    const formData = new FormData();
    formData.append('query', query);
  
    try {
      const response = await axios.post(API_URL, formData, {
        // headers: { 'Content-Type': 'multipart/form-data' } // axios 通常会自动处理 FormData
      });
  
      if (response.data && response.data.answer) {
        messages.value.push({ sender: 'bot', text: response.data.answer });
      } else if (response.data && response.data.message) {
        messages.value.push({ sender: 'bot', text: response.data.message });
      } else {
        messages.value.push({ sender: 'bot', text: '抱歉，未能获取到有效的回答格式。' });
      }
    } catch (error) {
      console.error('API请求错误:', error);
      let errorMessage = '抱歉，与服务器通信时发生错误。';
      if (error.response && error.response.data && error.response.data.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = `错误: ${error.response.data.detail}`;
        } else if (Array.isArray(error.response.data.detail) && error.response.data.detail.length > 0 && error.response.data.detail[0].msg) {
          errorMessage = `输入错误: ${error.response.data.detail[0].msg}`;
        }
      } else if (error.message) {
          errorMessage = `网络或请求错误: ${error.message}`;
      }
      messages.value.push({ sender: 'bot', text: errorMessage });
    } finally {
      isLoading.value = false;
      scrollToBottom();
    }
  };
  </script>
  
  <style scoped>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 80vh;
    max-width: 700px;
    min-width: 350px;
    margin: 20px auto;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    background-color: #ffffff;
    overflow: hidden;
  }
  
  .chat-box {
    flex-grow: 1;
    padding: 20px;
    overflow-y: auto;
    background-color: #f9f9f9;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .message-bubble {
    display: inline-block;
    clear: both;
    margin-bottom: 15px;
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 75%;
    word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  
  .message-bubble p:first-child { /* 发送者名称样式 */
    font-weight: bold;
    margin-bottom: 4px;
    font-size: 0.9em;
    color: #555;
  }
  
  /* --- 4. 为 Markdown 内容添加一个容器样式 (可选) --- */
  .markdown-content {
    line-height: 1.6; /* Markdown 内容通常需要更好的行高 */
    white-space: pre-wrap; /* 保留 Markdown 生成的换行和空格 */
  }
  /* 你可能还需要为 Markdown 生成的特定 HTML 标签（如 h1, h2, ul, li, code, blockquote 等）添加样式 */
  .markdown-content :deep(h1), .markdown-content :deep(h2), .markdown-content :deep(h3) {
    margin-top: 0.8em;
    margin-bottom: 0.4em;
    line-height: 1.2;
  }
  .markdown-content :deep(ul), .markdown-content :deep(ol) {
    padding-left: 20px;
  }
  .markdown-content :deep(li) {
    margin-bottom: 0.2em;
  }
  .markdown-content :deep(p) {
    margin-top: 0;
    margin-bottom: 0.5em;
  }
  .markdown-content :deep(pre) { /* 代码块样式 */
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
  }
  .markdown-content :deep(code) { /*行内代码样式 */
    background-color: #f0f0f0;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  }
  
  
  .user-message {
    background-color: #007bff;
    color: white;
    float: right;
    margin-left: 25%;
    border-bottom-right-radius: 5px;
  }
  .user-message p:first-child {
    color: #e0e0e0;
  }
  
  
  .bot-message {
    background-color: #e9ecef;
    color: #212529;
    float: left;
    margin-right: 25%;
    border-bottom-left-radius: 5px;
  }
  .bot-message p:first-child { /* AI 发送者名称 */
    color: #007bff;
  }
  .bot-message .markdown-content :deep(p):first-child { /* 修正：如果Markdown内容以<p>开头，可能不需要额外的上边距 */
      margin-top: 0;
  }
  
  
  .input-area {
    display: flex;
    padding: 15px;
    border-top: 1px solid #e0e0e0;
    background-color: #f8f9fa;
  }
  
  .input-area input {
    flex-grow: 1;
    padding: 12px 15px;
    border: 1px solid #ced4da;
    border-radius: 20px;
    margin-right: 10px;
    font-size: 1em;
    outline: none;
  }
  .input-area input:focus {
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
  }
  
  .input-area button {
    padding: 12px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.2s ease-in-out;
  }
  
  .input-area button:hover:not(:disabled) {
    background-color: #0056b3;
  }
  .input-area button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  </style>