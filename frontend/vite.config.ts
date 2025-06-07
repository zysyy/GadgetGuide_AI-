/// <reference types="node" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'         // ⬅️ 新增

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),  // ⬅️ 这样 @ 代表 src
    },
  },
})
