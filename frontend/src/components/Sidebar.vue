<!-- src/components/Sidebar.vue -->
<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span>会话列表</span>
      <button class="add-btn" @click="$emit('new-conversation')" aria-label="新建会话">
        <svg width="22" height="22" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="10" fill="#3573fa"/>
          <rect x="9" y="5" width="2" height="10" rx="1" fill="white"/>
          <rect x="5" y="9" width="10" height="2" rx="1" fill="white"/>
        </svg>
      </button>
    </div>
    <ul class="conversation-list">
      <li
        v-for="(conv, i) in conversations"
        :key="i"
        :class="{ active: i === currentIndex }"
        @click="select(i)"
        @mouseenter="hoverIndex = i"
        @mouseleave="hoverIndex = null"
        @dblclick.stop="startEdit(i, conv)"
      >
        <!-- 编辑态 -->
        <template v-if="editIndex === i">
          <input
            v-model="editName"
            ref="editInput"
            @blur="finishEdit(i)"
            @keyup.enter="finishEdit(i)"
            @keyup.esc="cancelEdit"
            class="rename-input"
            maxlength="30"
          />
        </template>
        <!-- 展示态 -->
        <template v-else>
          <span>{{ conv }}</span>
          <span class="edit-btn" @click.stop="startEdit(i, conv)" title="重命名">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
              <path d="M3 17h14M13.5 3.5a2 2 0 0 1 2.8 2.8l-8.2 8.2L5 15l0.5-3.1 8-8z" stroke="#3573fa" stroke-width="1.5"/>
            </svg>
          </span>
          <button
            v-if="hoverIndex === i"
            class="delete-btn"
            @click.stop="deleteConv(i)"
            title="删除会话"
            aria-label="删除"
          >×</button>
        </template>
      </li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
const props = defineProps<{
  conversations: string[]
  currentIndex: number
}>()
const emits = defineEmits<{
  (event: 'update:currentIndex', value: number): void
  (event: 'new-conversation'): void
  (event: 'delete-conversation', value: number): void
  (event: 'rename', i: number, name: string): void
}>()

const hoverIndex = ref<number | null>(null)

function select(i: number) {
  emits('update:currentIndex', i)
}
function deleteConv(i: number) {
  emits('delete-conversation', i)
}

// ----------- 重命名核心 -----------
const editIndex = ref<number | null>(null)
const editName = ref('')
const editInput = ref<HTMLInputElement>()

function startEdit(i: number, name: string) {
  editIndex.value = i
  editName.value = name
  nextTick(() => editInput.value?.focus())
}
function finishEdit(i: number) {
  const name = editName.value.trim() || '未命名会话'
  emits('rename', i, name)
  editIndex.value = null
  editName.value = ''
}
function cancelEdit() {
  editIndex.value = null
  editName.value = ''
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: var(--color-sidebar);
  border-right: 1px solid var(--color-border);
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  transition: background 0.3s, color 0.3s, border-color 0.2s;
}

.sidebar-header {
  display: flex;
  align-items: center;         
  justify-content: space-between;
  font-weight: bold;
  font-size: 17px;
  height: 40px;                
  padding: 0 18px 10px 24px;   
  box-sizing: border-box;
  color: var(--color-main);
}

.add-btn {
  background: none;
  border: none;
  outline: none;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  height: 32px;
  width: 32px;
  transition: background 0.15s;
}
.add-btn:hover {
  background: var(--color-bot);
}

.conversation-list {
  list-style: none;
  margin: 0;
  padding: 0 12px;
  flex: 1;
  overflow-y: auto;
}
.conversation-list li {
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  background: none;
  transition: background 0.15s, color 0.2s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--color-main);
}
.conversation-list li.active,
.conversation-list li:hover {
  background: var(--color-bot);
  color: var(--color-link);
}
.delete-btn {
  background: none;
  border: none;
  color: #bbb;
  font-size: 18px;
  margin-left: 8px;
  cursor: pointer;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  line-height: 18px;
  transition: background 0.2s, color 0.2s;
  vertical-align: middle;
  padding: 0;
}
.delete-btn:hover {
  color: #fff;
  background: #ff5959;
}
.rename-input {
  width: 80%;
  padding: 5px 8px;
  border: 1px solid var(--color-link);
  border-radius: 6px;
  font-size: 15px;
  margin-right: 6px;
  outline: none;
  background: var(--color-sidebar);
  color: var(--color-main);
  transition: background 0.2s, color 0.2s;
}
.edit-btn {
  margin-left: 8px;
  cursor: pointer;
  vertical-align: middle;
  opacity: 0.5;
  transition: opacity 0.2s;
  display: inline-flex;
  align-items: center;
}
.conversation-list li:hover .edit-btn,
.conversation-list li.active .edit-btn {
  opacity: 1;
}
</style>
