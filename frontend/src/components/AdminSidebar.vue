<!-- src/components/AdminSidebar.vue -->
<template>
  <aside class="admin-sidebar">
    <ul>
      <li>
        <router-link to="/admin" exact-active-class="active">后台首页</router-link>
      </li>
      <li>
        <router-link to="/admin/users" exact-active-class="active">用户管理</router-link>
      </li>
      <li>
        <router-link to="/admin/kb" exact-active-class="active">知识库管理</router-link>
      </li>
      <li>
        <router-link to="/admin/stats" exact-active-class="active">热词统计</router-link>
      </li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
// 绝不要 import AdminSidebar 自己！！！
</script>

<style scoped>
.admin-sidebar {
  width: 200px;
  background: var(--color-sidebar, #1e1e2f); /* 默认深色背景 */
  border-right: 1px solid var(--color-border, #333);
  padding: 40px 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05);
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
}

li {
  width: 100%;
  margin-bottom: 12px; /* 让列表更紧凑些 */
}

.router-link-exact-active,
.active {
  color: var(--color-primary, #42b983);
  font-weight: 600;
  border-left: 4px solid var(--color-primary, #42b983);
  background: rgba(66, 185, 131, 0.15); /* 选中项背景略深，更明显 */
}

a {
  display: block;
  width: 100%;
  padding: 10px 18px; /* 轻微增加左右内边距，手感更舒适 */
  color: var(--color-text, #ccc); /* 微调文字色，浅色模式更清晰 */
  text-decoration: none;
  border-radius: 4px;
  transition: background 0.2s ease, color 0.2s ease;
}

a:hover {
  background: rgba(255, 255, 255, 0.08); /* 悬停效果更柔和 */
  color: var(--color-link-hover, #fff);
}

@media (prefers-color-scheme: light) {
  .admin-sidebar {
    background: #f9f9f9; /* 浅色背景适配 */
    border-right: 1px solid #ddd;
  }

  .router-link-exact-active,
  .active {
    background: rgba(66, 185, 131, 0.15);
    color: var(--color-primary, #42b983);
  }

  a {
    color: #444; /* 浅色模式下深色文字，更可读 */
  }

  a:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #000;
  }
}
</style>
