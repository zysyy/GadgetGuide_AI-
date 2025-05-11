<template>
    <div class="uploader-container">
      <h3>知识库文档上传</h3>
      <div class="upload-controls">
        <label for="file-upload" class="file-upload-label">
          选择文件
        </label>
        <input
          id="file-upload"
          type="file"
          @change="handleFileSelect"
          multiple
          accept=".txt,.pdf,.docx,.md" 
          ref="fileInputRef"
        />
        <button @click="uploadDocuments" :disabled="selectedFiles.length === 0 || isLoading" class="upload-button">
          <span v-if="isLoading">上传中...</span>
          <span v-else>上传选中文件 ({{ selectedFiles.length }})</span>
        </button>
      </div>
  
      <div v-if="selectedFiles.length > 0" class="selected-files-preview">
        <h4>已选择的文件：</h4>
        <ul>
          <li v-for="file in selectedFiles" :key="file.name">
            {{ file.name }} ({{ formatFileSize(file.size) }})
          </li>
        </ul>
      </div>
  
      <div v-if="uploadMessage" :class="['upload-status', uploadError ? 'error' : 'success']">
        <p>{{ uploadMessage }}</p>
        <ul v-if="processedFilesDetails.length > 0">
          <li v-for="detail in processedFilesDetails" :key="detail.filename">
            {{ detail.filename }}: {{ detail.status }} 
            <span v-if="detail.error" class="error-detail"> - 错误: {{ detail.error }}</span>
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import axios from 'axios';
  
  const selectedFiles = ref([]); // 存储用户选择的文件对象列表
  const isLoading = ref(false);   // 上传状态
  const uploadMessage = ref('');  // 上传结果消息
  const uploadError = ref(false); // 标志上传结果是否为错误
  const processedFilesDetails = ref([]); // 存储后端返回的每个文件的处理详情
  const fileInputRef = ref(null); // 用于清空文件选择框
  
  // 后端 API 地址
  const API_UPLOAD_URL = 'http://127.0.0.1:8000/upload-documents/'; // 您的 FastAPI 后端上传端点
  
  const handleFileSelect = (event) => {
    // event.target.files 是一个 FileList 对象，需要转换为数组
    selectedFiles.value = Array.from(event.target.files);
    uploadMessage.value = ''; // 清空之前的上传消息
    uploadError.value = false;
    processedFilesDetails.value = [];
  };
  
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  const uploadDocuments = async () => {
    if (selectedFiles.value.length === 0 || isLoading.value) return;
  
    isLoading.value = true;
    uploadMessage.value = '正在上传并处理文件...';
    uploadError.value = false;
    processedFilesDetails.value = [];
  
    const formData = new FormData();
    selectedFiles.value.forEach(file => {
      formData.append('files', file); // 后端 FastAPI 端点期望的参数名是 'files'
    });
  
    try {
      const response = await axios.post(API_UPLOAD_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data', // 通常 axios 会为 FormData 自动设置
        },
        // 可选：监听上传进度
        // onUploadProgress: progressEvent => {
        //   const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        //   uploadMessage.value = `上传中... ${percentCompleted}%`;
        // }
      });
  
      if (response.data) {
        uploadMessage.value = response.data.message || '文件处理完成！';
        uploadError.value = false; // 假设成功
        if (response.data.processed_files_details) {
          processedFilesDetails.value = response.data.processed_files_details;
        }
         // 清空已选择的文件，以便用户可以重新选择
        selectedFiles.value = [];
        if(fileInputRef.value) {
          fileInputRef.value.value = null; // 重置文件输入框
        }
      } else {
        uploadMessage.value = '上传成功，但服务器未返回明确的处理信息。';
        uploadError.value = true;
      }
  
    } catch (error) {
      console.error('文件上传或处理错误:', error);
      uploadError.value = true;
      if (error.response && error.response.data && error.response.data.detail) {
        uploadMessage.value = `上传失败: ${error.response.data.detail}`;
      } else if (error.message) {
        uploadMessage.value = `上传失败: ${error.message}`;
      } else {
        uploadMessage.value = '上传失败，发生未知错误。';
      }
      // 如果需要，可以在这里显示更详细的错误信息或后端返回的 processed_files_details
      if (error.response && error.response.data && error.response.data.processed_files_details) {
          processedFilesDetails.value = error.response.data.processed_files_details;
      } else if (error.response && error.response.data && error.response.data.headers && error.response.data.headers['X-Processed-Files-Details']) {
          try {
              processedFilesDetails.value = JSON.parse(error.response.data.headers['X-Processed-Files-Details']);
          } catch (e) { /* ignore parsing error */ }
      }
    } finally {
      isLoading.value = false;
    }
  };
  </script>
  
  <style scoped>
  /* 使用您在 theme.css 中定义的全局 CSS 变量 */
  .uploader-container {
    background-color: var(--color-background-container, #fff);
    padding: calc(var(--spacing-unit, 8px) * 3);
    border-radius: var(--border-radius-large, 12px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-top: calc(var(--spacing-unit, 8px) * 2);
    border: 1px solid var(--color-border, #e0e0e0);
  }
  
  .uploader-container h3 {
    margin-top: 0;
    margin-bottom: calc(var(--spacing-unit, 8px) * 2);
    color: var(--color-primary-deep-blue, #1f3a5b);
    text-align: center;
  }
  
  .upload-controls {
    display: flex;
    align-items: center;
    gap: calc(var(--spacing-unit, 8px) * 2); /* 控件之间的间隙 */
    margin-bottom: calc(var(--spacing-unit, 8px) * 2);
  }
  
  .file-upload-label {
    padding: calc(var(--spacing-unit, 8px) * 1.25) calc(var(--spacing-unit, 8px) * 2);
    background-color: var(--color-primary-light-blue, #5db3d5);
    color: var(--color-text-on-primary, white);
    border-radius: var(--border-radius-medium, 8px);
    cursor: pointer;
    transition: background-color var(--transition-short, 0.2s ease-in-out);
    font-weight: 500;
    text-align: center;
  }
  .file-upload-label:hover {
    background-color: color-mix(in srgb, var(--color-primary-light-blue, #5db3d5) 85%, black);
  }
  
  /* 隐藏原生的文件输入框，我们用 label 来触发它 */
  #file-upload {
    display: none;
  }
  
  .upload-button {
    padding: calc(var(--spacing-unit, 8px) * 1.25) calc(var(--spacing-unit, 8px) * 2.5);
    background-color: var(--color-accent-green, #a1d69f);
    color: var(--color-text-on-accent-green, var(--color-primary-deep-blue, #1f3a5b));
    border: none;
    border-radius: var(--border-radius-medium, 8px);
    cursor: pointer;
    font-size: 1em;
    font-weight: 500;
    transition: background-color var(--transition-short, 0.2s ease-in-out);
  }
  
  .upload-button:hover:not(:disabled) {
    background-color: color-mix(in srgb, var(--color-accent-green, #a1d69f) 85%, black);
  }
  .upload-button:disabled {
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
  }
  
  .selected-files-preview {
    margin-top: calc(var(--spacing-unit, 8px) * 2);
    padding: var(--spacing-unit, 8px);
    background-color: var(--color-background-page, #f0f2f5);
    border-radius: var(--border-radius-small, 4px);
    border: 1px dashed var(--color-border, #e0e0e0);
  }
  .selected-files-preview h4 {
    margin-top: 0;
    margin-bottom: var(--spacing-unit, 8px);
    font-size: 0.9em;
    color: var(--color-text-secondary, #555);
  }
  .selected-files-preview ul {
    list-style-type: none;
    padding-left: 0;
    margin: 0;
  }
  .selected-files-preview li {
    padding: calc(var(--spacing-unit, 8px) * 0.5) 0;
    font-size: 0.85em;
    border-bottom: 1px solid color-mix(in srgb, var(--color-border, #e0e0e0) 50%, transparent);
  }
  .selected-files-preview li:last-child {
    border-bottom: none;
  }
  
  .upload-status {
    margin-top: calc(var(--spacing-unit, 8px) * 2);
    padding: var(--spacing-unit, 8px);
    border-radius: var(--border-radius-small, 4px);
    font-weight: 500;
  }
  .upload-status.success {
    background-color: color-mix(in srgb, var(--color-accent-green, #a1d69f) 30%, transparent);
    color: var(--color-primary-deep-blue, #1f3a5b);
    border: 1px solid var(--color-accent-green, #a1d69f);
  }
  .upload-status.error {
    background-color: color-mix(in srgb, var(--color-accent-yellow, #f1c40e) 20%, transparent);
    color: color-mix(in srgb, var(--color-accent-yellow, #f1c40e) 100%, black 30%);
    border: 1px solid var(--color-accent-yellow, #f1c40e);
  }
  .upload-status p {
      margin-bottom: calc(var(--spacing-unit, 8px) * 0.5);
  }
  .upload-status ul {
      font-size: 0.9em;
      padding-left: calc(var(--spacing-unit, 8px) * 2);
      margin: 0;
  }
  .upload-status .error-detail {
      color: red; /* 或者一个来自主题的错误色 */
      font-style: italic;
  }
  </style>