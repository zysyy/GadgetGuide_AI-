<!-- src/views/admin/AdminHome.vue -->
<template>
  <div class="admin-home">
    <h2>欢迎来到后台管理中心</h2>
    <p>这里是 GadgetGuide AI 的管理后台。您可以通过左侧菜单快速进入各功能模块：</p>

    <ul class="features-list">
      <li>
        <strong>用户管理：</strong> 查看和管理所有注册用户，支持查看用户会话详情。
      </li>
      <li>
        <strong>知识库管理：</strong> 上传或删除文档，自动更新知识库索引。
      </li>
      <li>
        <strong>热词统计：</strong> 分析和展示热门词汇，支持词云可视化。
      </li>
      <li>
        <strong>后台首页：</strong> 后台概况，后续可支持公告发布、系统状态等展示。
      </li>
    </ul>

    <p>如果您在使用过程中遇到任何问题或需要帮助，请随时联系技术支持。</p>
  </div>
</template>

<script setup lang="ts">
// 这里只是简单的欢迎页，后续可根据需要添加更多系统信息和公告。
</script>

<style scoped>
.admin-home {
  padding: 20px;
  color: #333; /* 浅色模式下：深灰色 */
}

.admin-home h2 {
  margin-bottom: 10px;
  font-size: 1.5em;
  color: var(--color-primary, #42b983);
}

.features-list {
  margin-top: 10px;
  list-style: disc inside;
  line-height: 1.6;
  color: #555; /* 浅色模式下：二级文字深灰色 */
}

.features-list li {
  margin-bottom: 6px;
}

/* ====== 深色模式：提升对比度 ====== */
:root.dark .admin-home {
  color: #ddd; /* 深色模式下：主文字更亮 */
}

:root.dark .features-list {
  color: #bbb; /* 深色模式下：二级文字更亮 */
}
</style>
