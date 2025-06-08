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
  width: 180px;
  background: var(--color-sidebar);
  border-right: 1px solid var(--color-border);
  padding-top: 38px;
}
ul {
  padding: 0 0 0 16px;
  margin: 0;
}
li {
  margin-bottom: 22px;
}
.router-link-exact-active,
.active {
  color: var(--color-link);
  font-weight: bold;
}
</style>
