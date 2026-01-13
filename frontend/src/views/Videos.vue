<template>
  <div>
    <el-card>
      <!-- 搜索栏 -->
      <div style="margin-bottom: 20px; display: flex; gap: 10px">
        <el-select v-model="filters.platform" placeholder="平台" clearable style="width: 150px">
          <el-option label="抖音" value="douyin" />
          <el-option label="快手" value="kuaishou" />
          <el-option label="小红书" value="xiaohongshu" />
        </el-select>
        
        <el-select v-model="filters.risk_level" placeholder="风险等级" clearable style="width: 150px">
          <el-option label="高风险" value="high" />
          <el-option label="中风险" value="medium" />
          <el-option label="低风险" value="low" />
          <el-option label="安全" value="safe" />
        </el-select>
        
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 150px">
          <el-option label="已检测" value="detected" />
          <el-option label="已分析" value="analyzed" />
          <el-option label="待举报" value="pending_report" />
          <el-option label="已举报" value="reported" />
          <el-option label="已下架" value="takedown" />
        </el-select>
        
        <el-button type="primary" @click="fetchVideos">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <!-- 视频列表 -->
      <el-table :data="videos" stripe v-loading="loading">
        <el-table-column prop="video_id" label="视频ID" width="180" />
        <el-table-column prop="title" label="标题" width="300" show-overflow-tooltip />
        <el-table-column prop="platform" label="平台" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ platformMap[row.platform] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="riskTypeMap[row.risk_level]" size="small">
              {{ riskLevelMap[row.risk_level] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="risk_score" label="风险评分" width="100">
          <template #default="{ row }">
            {{ row.risk_score ? row.risk_score.toFixed(3) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]" size="small">
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detected_time" label="检测时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="primary" @click="analyzeVideo(row)" :disabled="row.risk_level">分析</el-button>
            <el-button size="small" type="danger" @click="reportVideo(row)" :disabled="row.status === 'reported'">举报</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top: 20px; text-align: right">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.limit"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchVideos"
          @current-change="fetchVideos"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="视频详情" width="800px">
      <el-descriptions :column="2" border v-if="currentVideo">
        <el-descriptions-item label="视频ID">{{ currentVideo.video_id }}</el-descriptions-item>
        <el-descriptions-item label="平台">{{ platformMap[currentVideo.platform] }}</el-descriptions-item>
        <el-descriptions-item label="标题" :span="2">{{ currentVideo.title }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentVideo.description }}</el-descriptions-item>
        <el-descriptions-item label="作者">{{ currentVideo.author }}</el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <el-tag :type="riskTypeMap[currentVideo.risk_level]">
            {{ riskLevelMap[currentVideo.risk_level] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险评分">{{ currentVideo.risk_score }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTypeMap[currentVideo.status]">
            {{ statusMap[currentVideo.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="检测时间">{{ currentVideo.detected_time }}</el-descriptions-item>
        <el-descriptions-item label="举报时间">{{ currentVideo.reported_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="下架时间">{{ currentVideo.takedown_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="是否下架">
          <el-tag :type="currentVideo.is_takedown ? 'success' : 'info'">
            {{ currentVideo.is_takedown ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const videos = ref([])
const detailVisible = ref(false)
const currentVideo = ref(null)

const filters = reactive({
  platform: '',
  risk_level: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

const platformMap = {
  'douyin': '抖音',
  'kuaishou': '快手',
  'xiaohongshu': '小红书'
}

const riskLevelMap = {
  'high': '高风险',
  'medium': '中风险',
  'low': '低风险',
  'safe': '安全'
}

const riskTypeMap = {
  'high': 'danger',
  'medium': 'warning',
  'low': 'info',
  'safe': 'success'
}

const statusMap = {
  'detected': '已检测',
  'analyzed': '已分析',
  'pending_report': '待举报',
  'reported': '已举报',
  'takedown': '已下架'
}

const statusTypeMap = {
  'detected': 'info',
  'analyzed': '',
  'pending_report': 'warning',
  'reported': 'danger',
  'takedown': 'success'
}

// 获取视频列表
const fetchVideos = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit,
      ...filters
    }
    
    const res = await axios.get('/api/v1/videos', { params })
    videos.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    ElMessage.error('获取视频列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilters = () => {
  filters.platform = ''
  filters.risk_level = ''
  filters.status = ''
  pagination.page = 1
  fetchVideos()
}

// 查看详情
const viewDetail = (row) => {
  currentVideo.value = row
  detailVisible.value = true
}

// 分析视频
const analyzeVideo = async (row) => {
  try {
    await axios.post('/api/v1/videos/analyze', { video_id: row.video_id })
    ElMessage.success('分析任务已提交')
    setTimeout(fetchVideos, 2000)
  } catch (error) {
    ElMessage.error('分析失败')
  }
}

// 举报视频
const reportVideo = async (row) => {
  try {
    await axios.post('/api/v1/videos/report', { video_id: row.video_id })
    ElMessage.success('举报任务已提交')
    setTimeout(fetchVideos, 2000)
  } catch (error) {
    ElMessage.error('举报失败')
  }
}

onMounted(() => {
  fetchVideos()
})
</script>
