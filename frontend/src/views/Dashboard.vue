<template>
  <div>
    <!-- 数据卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <div>
              <div style="color: #909399; font-size: 14px">总视频数</div>
              <div style="font-size: 28px; font-weight: bold; margin-top: 10px">{{ systemInfo.total_videos }}</div>
            </div>
            <el-icon :size="40" color="#409EFF"><VideoCamera /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <div>
              <div style="color: #909399; font-size: 14px">待举报</div>
              <div style="font-size: 28px; font-weight: bold; margin-top: 10px; color: #E6A23C">{{ systemInfo.pending_report }}</div>
            </div>
            <el-icon :size="40" color="#E6A23C"><Warning /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <div>
              <div style="color: #909399; font-size: 14px">已举报</div>
              <div style="font-size: 28px; font-weight: bold; margin-top: 10px; color: #F56C6C">{{ systemInfo.reported }}</div>
            </div>
            <el-icon :size="40" color="#F56C6C"><Bell /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <div>
              <div style="color: #909399; font-size: 14px">已下架</div>
              <div style="font-size: 28px; font-weight: bold; margin-top: 10px; color: #67C23A">{{ systemInfo.takedown }}</div>
            </div>
            <el-icon :size="40" color="#67C23A"><CircleCheck /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>风险等级分布</span>
              <el-tag size="small" type="info">最近7天</el-tag>
            </div>
          </template>
          <div ref="riskChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>平台数据对比</span>
              <el-tag size="small" type="info">最近7天</el-tag>
            </div>
          </template>
          <div ref="platformChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近任务执行 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>最近任务执行</span>
      </template>
      <el-table :data="recentTasks" stripe>
        <el-table-column prop="task_name" label="任务名称" width="200" />
        <el-table-column prop="start_time" label="执行时间" width="180" />
        <el-table-column prop="duration" label="耗时(秒)" width="100" />
        <el-table-column prop="items_processed" label="处理数量" width="100" />
        <el-table-column prop="success" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { VideoCamera, Warning, Bell, CircleCheck } from '@element-plus/icons-vue'

const systemInfo = ref({
  total_videos: 0,
  pending_report: 0,
  reported: 0,
  takedown: 0
})

const statistics = ref({})
const recentTasks = ref([])
const riskChart = ref(null)
const platformChart = ref(null)

// 获取系统信息
const fetchSystemInfo = async () => {
  try {
    const res = await axios.get('/api/v1/system/info')
    if (res.data.code === 200) {
      systemInfo.value = res.data.data
    }
  } catch (error) {
    console.error('获取系统信息失败:', error)
  }
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const res = await axios.get('/api/v1/statistics/overview?days=7')
    statistics.value = res.data
    initCharts()
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取任务日志
const fetchTaskLogs = async () => {
  try {
    const res = await axios.get('/api/v1/tasks/logs?limit=10')
    recentTasks.value = res.data
  } catch (error) {
    console.error('获取任务日志失败:', error)
  }
}

// 初始化图表
const initCharts = () => {
  // 风险等级分布饼图
  if (riskChart.value) {
    const chart = echarts.init(riskChart.value)
    chart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        bottom: '5%',
        left: 'center'
      },
      series: [
        {
          name: '风险等级',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 20,
              fontWeight: 'bold'
            }
          },
          data: [
            { value: statistics.value.high_risk_videos || 0, name: '高风险', itemStyle: { color: '#F56C6C' } },
            { value: statistics.value.medium_risk_videos || 0, name: '中风险', itemStyle: { color: '#E6A23C' } },
            { value: statistics.value.low_risk_videos || 0, name: '低风险', itemStyle: { color: '#409EFF' } }
          ]
        }
      ]
    })
  }

  // 平台数据柱状图
  if (platformChart.value) {
    const chart = echarts.init(platformChart.value)
    const platforms = statistics.value.platforms || {}
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: Object.keys(platforms)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '视频数量',
          type: 'bar',
          data: Object.values(platforms),
          itemStyle: {
            color: '#409EFF',
            borderRadius: [5, 5, 0, 0]
          }
        }
      ]
    })
  }
}

onMounted(() => {
  fetchSystemInfo()
  fetchStatistics()
  fetchTaskLogs()

  // 定时刷新
  setInterval(() => {
    fetchSystemInfo()
  }, 30000) // 每30秒刷新一次
})
</script>
