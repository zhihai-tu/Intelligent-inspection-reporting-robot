<template>
  <div id="app">
    <el-container style="height: 100vh">
      <!-- 侧边栏 -->
      <el-aside width="250px" style="background-color: #304156">
        <div style="padding: 20px; color: white; font-size: 18px; font-weight: bold; text-align: center">
          🤖 智能巡检机器人
        </div>
        <el-menu
          :default-active="activeMenu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="/videos">
            <el-icon><VideoCamera /></el-icon>
            <span>视频管理</span>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><PieChart /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><Clock /></el-icon>
            <span>任务管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header style="background-color: white; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between">
          <h2 style="margin: 0">{{ pageTitle }}</h2>
          <div>
            <el-tag type="success">运行中</el-tag>
            <span style="margin-left: 20px; color: #909399">{{ currentTime }}</span>
          </div>
        </el-header>

        <!-- 内容 -->
        <el-main style="background-color: #f0f2f5">
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { DataAnalysis, VideoCamera, PieChart, Clock } from '@element-plus/icons-vue'

const route = useRoute()
const currentTime = ref('')
const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/': '数据概览',
    '/videos': '视频管理',
    '/statistics': '统计分析',
    '/tasks': '任务管理'
  }
  return titles[route.path] || '智能巡检机器人'
})

// 更新当前时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

let timer = null
onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}
</style>
