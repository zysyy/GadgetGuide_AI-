<template>
  <div id="app">
    <header class="app-header">
      <h1>GadgetGuide AI</h1>
      </header>
    <main class="app-main">
      <ChatInterface />
    </main>
    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} GadgetGuide AI. All rights reserved (for demonstration).</p>
      </footer>
  </div>
</template>

<script setup>
// 导入我们的聊天界面组件
import ChatInterface from './components/ChatInterface.vue';

// 这里不需要额外的 JavaScript 逻辑，因为主要功能都在 ChatInterface 组件中
// 如果将来有全局应用级别的逻辑，可以写在这里
</script>

<style>
/* 全局样式或 App.vue 的特定样式 */
/* 为了避免样式冲突并保持组件的封装性，通常推荐将大部分样式
  写在各个组件内部的 <style scoped> 中。
  这里的样式是针对整个应用的根元素 #app 和一些基本布局。
*/

/* 重置一些默认样式，可选 */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif; /* 与 Vue 默认字体一致 */
  background-color: #f4f7f6; /* 给页面一个浅色背景 */
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* 让 #app 至少占据整个视口高度 */
  color: #2c3e50;
}

.app-header {
  background-color: #343a40; /* 深色页眉背景 */
  color: white;
  padding: 15px 30px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 1.8em;
}

.app-main {
  flex-grow: 1; /* 让主内容区域占据剩余空间 */
  padding: 20px; /* 给主内容区域一些内边距 */
  display: flex; /* 使用 flex 布局来居中聊天组件 */
  justify-content: center; /* 水平居中 */
  align-items: flex-start; /* 垂直方向上，如果内容不足，从顶部开始对齐 */
}

.app-footer {
  background-color: #343a40; /* 深色页脚背景 */
  color: #adb5bd; /* 页脚文字颜色浅一些 */
  text-align: center;
  padding: 15px;
  font-size: 0.85em;
  margin-top: auto; /* 将页脚推到底部，即使内容不足 */
}
</style>