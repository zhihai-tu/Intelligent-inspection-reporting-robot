import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'

// 导入页面组件
import Dashboard from './views/Dashboard.vue'
import Videos from './views/Videos.vue'
import Statistics from './views/Statistics.vue'
import Tasks from './views/Tasks.vue'

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/videos', component: Videos },
    { path: '/statistics', component: Statistics },
    { path: '/tasks', component: Tasks }
  ]
})

// 创建应用
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.mount('#app')
