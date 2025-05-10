<template>
  <div id="app">
    <header class="app-header">
      <h1>GadgetGuide AI</h1>
      </header>
    <main class="app-main">
      <ChatInterface />
    </main>
    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} GadgetGuide AI. (Demonstration Purposes)</p>
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
/* App.vue 的样式通常是全局的，或者只针对 #app 及其直接子元素的基础布局。
  我们在这里使用之前在 theme.css 中定义的 CSS 变量。
  确保 theme.css 已经在 main.js 中被正确导入。
*/

/* body, html 的基础样式已在 theme.css 中设置 (font-family, background-color) */

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* 让 #app 至少占据整个视口高度 */
  color: var(--color-text-primary); /* 全局主要文字颜色 */
}

.app-header {
  background-color: var(--color-primary-deep-blue); /* 使用深蓝色作为页眉背景 */
  color: var(--color-text-light); /* 页眉文字使用浅色 */
  padding: calc(var(--spacing-unit, 8px) * 2) calc(var(--spacing-unit, 8px) * 3); /* 使用间距变量 */
  text-align: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15); /* 稍微调整阴影 */
  border-bottom: 3px solid var(--color-primary-light-blue); /* 添加一个亮蓝色下边框增加层次感 */
}

.app-header h1 {
  margin: 0;
  font-size: 1.9em; /* 稍微增大标题 */
  font-weight: 600; /* 标题字重调整 */
}

.app-main {
  flex-grow: 1; /* 让主内容区域占据剩余空间 */
  padding: calc(var(--spacing-unit, 8px) * 2.5); /* 使用间距变量调整内边距 */
  display: flex;
  justify-content: center;
  align-items: flex-start; /* 或者 center, 确保聊天容器的对齐方式 */
  /* background-color: var(--color-background-page); /* 主内容区域背景已由body继承 */
}

.app-footer {
  background-color: var(--color-primary-medium-blue); /* 页脚使用中蓝色 */
  color: var(--color-accent-green); /* 页脚文字使用浅绿色，与深蓝背景形成对比 */
  /* 或者 color: color-mix(in srgb, var(--color-text-light) 80%, transparent); 更柔和的浅色 */
  text-align: center;
  padding: calc(var(--spacing-unit, 8px) * 1.5);
  font-size: 0.85em;
  margin-top: auto; /* 将页脚推到底部，即使内容不足 */
  border-top: 1px solid var(--color-primary-light-blue); /* 页脚上边框 */
}
</style>