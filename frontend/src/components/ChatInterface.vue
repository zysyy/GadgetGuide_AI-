<template>
    <div class="chat-container">
      <div class="chat-box" ref="chatBox">
        <div v-for="(message, index) in messages" :key="index"
             :class="['message-bubble', message.sender === 'user' ? 'user-message' : 'bot-message']">
          <p><strong>{{ message.sender === 'user' ? '您' : 'GadgetGuide AI' }}:</strong></p>
          <p>{{ message.text }}</p>
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
  import axios from 'axios'; // 确保您已经通过 npm install axios 安装了它
  
  // 响应式变量
  const userInput = ref(''); // 绑定到输入框的用户输入
  const messages = ref([]);  // 存储聊天记录的数组，格式: { sender: 'user'/'bot', text: '...' }
  const isLoading = ref(false); // API 请求的加载状态
  const chatBox = ref(null); // 对聊天框 DOM 元素的引用，用于自动滚动
  
  // 后端 API 地址 - 请确保这与您 FastAPI 后端的地址和端口一致
  const API_URL = 'http://127.0.0.1:8000/ask';
  
  // 辅助函数：在消息列表更新后自动滚动到底部
  const scrollToBottom = () => {
    nextTick(() => { // nextTick 确保 DOM 已经更新完毕
      if (chatBox.value) {
        chatBox.value.scrollTop = chatBox.value.scrollHeight;
      }
    });
  };
  
  // 发送消息的函数
  const sendMessage = async () => {
    const query = userInput.value.trim(); // 获取用户输入并去除首尾空格
    if (!query || isLoading.value) return; // 如果输入为空或正在加载中，则不执行
  
    isLoading.value = true; // 设置加载状态为 true
  
    // 1. 将用户输入添加到聊天记录中
    messages.value.push({ sender: 'user', text: query });
    userInput.value = ''; // 清空输入框
    scrollToBottom(); // 滚动到底部
  
    // 2. 准备发送给 FastAPI 后端的数据
    // FastAPI 的 Form(...) 参数通常需要 FormData 对象
    const formData = new FormData();
    formData.append('query', query);
  
    try {
      // 3. 发送 POST 请求到后端
      const response = await axios.post(API_URL, formData, {
        headers: {
          // FastAPI 使用 Form 时，axios 通常会自动设置正确的 Content-Type
          // 但如果遇到问题，可以尝试明确指定 'multipart/form-data'
          // 'Content-Type': 'multipart/form-data', 
        }
      });
  
      // 4. 处理后端响应
      if (response.data && response.data.answer) {
        messages.value.push({ sender: 'bot', text: response.data.answer });
      } else if (response.data && response.data.message) { // 兼容只返回 message 的情况
        messages.value.push({ sender: 'bot', text: response.data.message });
      }
      else {
        messages.value.push({ sender: 'bot', text: '抱歉，未能获取到有效的回答格式。' });
      }
    } catch (error) {
      console.error('API请求错误:', error);
      let errorMessage = '抱歉，与服务器通信时发生错误。';
      // 尝试从错误响应中获取更具体的错误信息
      if (error.response && error.response.data && error.response.data.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = `错误: ${error.response.data.detail}`;
        } else if (Array.isArray(error.response.data.detail) && error.response.data.detail.length > 0 && error.response.data.detail[0].msg) {
          // 处理 FastAPI 校验错误
          errorMessage = `输入错误: ${error.response.data.detail[0].msg}`;
        }
      } else if (error.message) {
          errorMessage = `网络或请求错误: ${error.message}`;
      }
      messages.value.push({ sender: 'bot', text: errorMessage });
    } finally {
      isLoading.value = false; // 请求完成后，设置加载状态为 false
      scrollToBottom(); // 再次滚动到底部，确保新消息可见
    }
  };
  </script>
  
  <style scoped>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 80vh; /* 或者您希望的聊天框高度 */
    max-width: 700px; /* 聊天框最大宽度 */
    min-width: 350px; /* 聊天框最小宽度 */
    margin: 20px auto; /* 页面居中显示 */
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    background-color: #ffffff;
    overflow: hidden; /* 确保子元素不会溢出圆角 */
  }
  
  .chat-box {
    flex-grow: 1; /* 占据剩余空间 */
    padding: 20px;
    overflow-y: auto; /* 内容超出时显示滚动条 */
    background-color: #f9f9f9; /* 聊天区域背景色 */
    border-bottom: 1px solid #e0e0e0;
  }
  
  .message-bubble {
    display: inline-block; /* 让气泡宽度自适应内容 */
    clear: both; /* 确保气泡不会互相重叠 */
    margin-bottom: 15px;
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 75%; /* 气泡最大宽度，避免太长 */
    word-wrap: break-word; /* 长单词或链接换行 */
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  
  .message-bubble p {
    margin: 0;
    line-height: 1.5; /* 增加行高，提升可读性 */
    white-space: pre-wrap; /* 保留换行符和空格 */
  }
  .message-bubble p:first-child { /* 发送者名称样式 */
    font-weight: bold;
    margin-bottom: 4px;
    font-size: 0.9em;
    color: #555;
  }
  
  .user-message {
    background-color: #007bff; /* 用户消息背景色 */
    color: white;
    float: right; /* 用户消息靠右 */
    margin-left: 25%; /* 确保不会占满整行 */
    border-bottom-right-radius: 5px; /* 调整气泡尖角效果 */
  }
  .user-message p:first-child {
    color: #e0e0e0; /* 用户名称颜色浅一点 */
  }
  
  
  .bot-message {
    background-color: #e9ecef; /* AI消息背景色 */
    color: #212529;
    float: left; /* AI消息靠左 */
    margin-right: 25%; /* 确保不会占满整行 */
    border-bottom-left-radius: 5px; /* 调整气泡尖角效果 */
  }
  .bot-message p:first-child {
    color: #007bff; /* AI名称颜色 */
  }
  
  
  .input-area {
    display: flex;
    padding: 15px;
    border-top: 1px solid #e0e0e0;
    background-color: #f8f9fa; /* 输入区域背景色 */
  }
  
  .input-area input {
    flex-grow: 1;
    padding: 12px 15px;
    border: 1px solid #ced4da;
    border-radius: 20px; /* 圆角输入框 */
    margin-right: 10px;
    font-size: 1em;
    outline: none; /* 去除点击时的默认边框 */
  }
  .input-area input:focus {
    border-color: #80bdff; /* 输入框获取焦点时的边框颜色 */
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25); /* 输入框获取焦点时的阴影 */
  }
  
  .input-area button {
    padding: 12px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 20px; /* 圆角按钮 */
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.2s ease-in-out; /* 过渡效果 */
  }
  
  .input-area button:hover:not(:disabled) {
    background-color: #0056b3; /* 按钮悬停颜色 */
  }
  .input-area button:disabled {
    background-color: #cccccc; /* 按钮禁用颜色 */
    cursor: not-allowed;
  }
  </style>