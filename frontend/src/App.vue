<template>
  <div id="app">
    <header class="app-header">
      <h1>GadgetGuide AI</h1>
      <nav class="app-nav">
        <router-link to="/chat">智能问答</router-link>
        <router-link to="/upload">文档管理</router-link>
        </nav>
    </header>
    <main class="app-main">
      <router-view /> 
    </main>
    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} GadgetGuide AI. (Demonstration Purposes)</p>
    </footer>
  </div>
</template>

<script setup>
// 当使用 Vue Router 时，App.vue 通常不需要再直接导入 ChatInterface 或 DocumentUploader。
// Vue Router 会根据当前的 URL 路径，自动将匹配到的组件渲染到 <router-view /> 的位置。
// 如果有全局的、与路由无关的逻辑，可以放在这里。
</script>

<style>
/* App.vue 的样式 (全局或基础布局) */
/* 使用您在 theme.css 中定义的 CSS 变量 */
/* 确保 theme.css 已经在 main.js 中被正确导入 */

/* body, html 的基础样式已在 theme.css 中设置 (font-family, background-color 等) */

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
  position: sticky; /* 让页眉在滚动时固定在顶部，可选 */
  top: 0;
  z-index: 1000; /* 确保页眉在最上层 */
}

.app-header h1 {
  margin: 0;
  font-size: 1.9em; /* 稍微增大标题 */
  font-weight: 600; /* 标题字重调整 */
  margin-bottom: calc(var(--spacing-unit, 8px) * 0.5); /* 为导航留出一点空间 */
}

/* 新增导航链接样式 */
.app-nav {
  margin-top: calc(var(--spacing-unit, 8px));
}

.app-nav a {
  font-weight: 500;
  color: var(--color-text-light);
  margin: 0 calc(var(--spacing-unit, 8px) * 1.5);
  text-decoration: none;
  padding: calc(var(--spacing-unit, 8px) * 0.75) var(--spacing-unit, 8px); /* 调整padding */
  border-radius: var(--border-radius-small, 4px);
  transition: background-color var(--transition-short, 0.2s ease-in-out), color var(--transition-short, 0.2s ease-in-out);
}

.app-nav a:hover {
  background-color: color-mix(in srgb, var(--color-primary-light-blue, #5db3d5) 25%, transparent); /* 悬停背景更柔和 */
}

.app-nav a.router-link-exact-active { /* 当前激活路由的链接样式 */
  color: var(--color-accent-yellow, #f1c40e);
  /* background-color: var(--color-primary-light-blue); */ /* 可以给激活链接一个更明显的背景 */
  font-weight: 700; /* 激活链接文字加粗 */
  pointer-events: none;
}

.app-main {
  flex-grow: 1;
  padding: calc(var(--spacing-unit, 8px) * 2.5);
  display: flex;
  justify-content: center;
  align-items: flex-start; 
  /* background-color: var(--color-background-page); /* 主内容区域背景已由body继承 */
}

.app-footer {
  background-color: var(--color-primary-medium-blue);
  color: var(--color-accent-green);
  text-align: center;
  padding: calc(var(--spacing-unit, 8px) * 1.5);
  font-size: 0.85em;
  margin-top: auto;
  border-top: 1px solid var(--color-primary-light-blue);
}

/* 页面切换过渡效果 (可选) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease; /* 过渡时间可以短一些 */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>