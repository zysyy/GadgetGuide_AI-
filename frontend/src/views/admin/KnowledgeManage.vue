<!-- src/views/admin/KnowledgeManage.vue -->
<template>
  <div>
    <h2>知识库管理</h2>

    <!-- 文件列表 -->
    <el-card style="margin-bottom: 18px;">
      <template #header>
        <span>已上传文件</span>
      </template>
      <el-table :data="files" style="width: 100%" v-loading="fileLoading" size="small">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="modified_at" label="上传/修改时间" width="170">
          <template #default="{ row }">
            {{ formatTime(row.modified_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteFile(row.filename)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="!files.length && !fileLoading" class="text-gray-400" style="padding: 18px; text-align: center;">
        暂无已上传文件
      </div>
    </el-card>

    <!-- 上传控件 -->
    <el-upload
      ref="upload"
      action=""
      :http-request="handleUpload"
      :show-file-list="false"
      multiple
      drag
      style="margin-bottom: 20px;"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">拖拽或点击上传文档（PDF/TXT/Word）</div>
    </el-upload>
    <el-alert
      v-if="uploadResult"
      :title="uploadResult"
      type="success"
      show-icon
      style="margin-bottom: 20px;"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_BASE = "http://localhost:8000"
const token = localStorage.getItem("token")

const files = ref<any[]>([])
const fileLoading = ref(false)
const uploadResult = ref("")

// 文件大小格式化
function formatSize(size: number) {
  if (size < 1024) return `${size}B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)}KB`
  return `${(size / 1024 / 1024).toFixed(1)}MB`
}
function formatTime(ts: number) {
  const d = new Date(ts * 1000)
  return d.toLocaleString()
}

// 加载文件列表
async function loadFiles() {
  fileLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/admin/uploaded-files`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error("获取文件列表失败")
    files.value = await res.json()
  } catch (e: any) {
    ElMessage.error(e.message || "网络错误")
    files.value = []
  } finally {
    fileLoading.value = false
  }
}

// 删除文件
async function deleteFile(filename: string) {
  ElMessageBox.confirm(
    `确定要删除文件「${filename}」吗？删除后索引会自动刷新！`,
    "提示",
    { type: "warning" }
  ).then(async () => {
    const res = await fetch(`${API_BASE}/admin/uploaded-files/${encodeURIComponent(filename)}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    })
    const data = await res.json()
    if (res.ok) {
      ElMessage.success(data.message || "文件已删除")
      loadFiles() // 刷新文件列表
    } else {
      ElMessage.error(data.detail || "删除失败")
    }
  }).catch(() => {})
}

// 上传文件
async function handleUpload(option: any) {
  const formData = new FormData()
  for (const file of option.fileList || [option.file]) {
    formData.append("files", file)
  }
  const res = await fetch(`${API_BASE}/admin/upload-documents/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })
  const data = await res.json()
  if (res.ok) {
    uploadResult.value = "知识库已更新！"
    ElMessage.success("上传成功，索引已刷新")
    loadFiles()
  } else {
    uploadResult.value = data.detail || "上传失败"
    ElMessage.error(uploadResult.value)
  }
}

onMounted(loadFiles)
</script>

<style scoped>
.text-gray-400 {
  color: #888;
}
</style>
