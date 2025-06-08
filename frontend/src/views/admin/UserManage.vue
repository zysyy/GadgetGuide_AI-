<!-- src/views/admin/UserManage.vue -->
<template>
  <div>
    <el-card>
      <template #header>
        <span>用户管理</span>
        <el-button type="primary" size="small" @click="loadUsers" style="float:right">刷新</el-button>
      </template>
      <el-table :data="users" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="is_admin" label="管理员" width="90">
          <template #default="scope">
            <el-tag :type="scope.row?.is_admin ? 'success' : 'info'">
              {{ scope.row?.is_admin ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" />
        <el-table-column label="操作" width="110">
          <template #default="scope">
            <el-button size="small" @click="showConvs(scope.row)">会话</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 会话弹窗 -->
    <el-dialog v-model="convDialogVisible" width="600px" :title="selectedUser ? `用户【${selectedUser.username}】的会话` : '会话列表'">
      <el-table :data="conversations" v-loading="convLoading">
        <el-table-column prop="id" label="会话ID" width="90" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="消息">
          <template #default="scope">
            <el-button size="small" @click="showMsgs(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 消息弹窗 -->
    <el-dialog v-model="msgDialogVisible" width="700px" title="消息记录">
      <el-table :data="messages" v-loading="msgLoading">
        <el-table-column prop="id" label="ID" width="60"/>
        <el-table-column prop="role" label="角色" width="80"/>
        <el-table-column prop="content" label="内容"/>
        <el-table-column prop="created_at" label="时间" width="170"/>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
console.log('UserManage.vue 被加载')

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// === 配置 ===
const API_BASE = "http://localhost:8000"
const token = localStorage.getItem("token") || ""

// === 状态 ===
const users = ref<any[]>([])
const loading = ref(false)

const conversations = ref<any[]>([])
const convDialogVisible = ref(false)
const convLoading = ref(false)
const selectedUser = ref<any>(null)

const messages = ref<any[]>([])
const msgDialogVisible = ref(false)
const msgLoading = ref(false)

// === 加载用户 ===
async function loadUsers() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/admin/users`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error("获取用户失败")
    users.value = await res.json()
  } catch (e: any) {
    ElMessage.error(e.message || "网络错误")
    users.value = []
  } finally {
    loading.value = false
  }
}
onMounted(loadUsers)

// === 查看会话 ===
async function showConvs(user: any) {
  selectedUser.value = user
  convDialogVisible.value = true
  convLoading.value = true
  conversations.value = [] // 防止旧数据残留
  try {
    const res = await fetch(`${API_BASE}/admin/users/${user.id}/conversations`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error("获取会话失败")
    conversations.value = await res.json()
  } catch (e: any) {
    ElMessage.error(e.message || "网络错误")
    conversations.value = []
  } finally {
    convLoading.value = false
  }
}

// === 查看消息 ===
async function showMsgs(conv: any) {
  msgDialogVisible.value = true
  msgLoading.value = true
  messages.value = []
  try {
    const res = await fetch(`${API_BASE}/admin/conversations/${conv.id}/messages`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error("获取消息失败")
    messages.value = await res.json()
  } catch (e: any) {
    ElMessage.error(e.message || "网络错误")
    messages.value = []
  } finally {
    msgLoading.value = false
  }
}
</script>

<style scoped>
.el-card {
  margin-bottom: 24px;
}
.el-table th, .el-table td {
  font-size: 15px;
}
</style>
