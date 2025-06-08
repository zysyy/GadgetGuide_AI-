// frontend/src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// 1. 引入 Element Plus 及其样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import './style.css'

const app = createApp(App)
app.use(router)
app.use(createPinia())
app.use(ElementPlus)  // ★★★ 注册 Element Plus！必须

app.mount('#app')
