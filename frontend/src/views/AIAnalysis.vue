<template>
  <div class="ai-analysis-container">
    <div class="header">
      <h2>AI股票分析</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="analysis-form">
          <template #header>
            <div class="card-header">
              <span>分析配置</span>
            </div>
          </template>
          <el-form :model="form" label-width="80px">
            <el-form-item label="股票">
              <el-input v-model="form.stock_code" placeholder="如: 000001" clearable />
            </el-form-item>
            <el-form-item label="分析类型">
              <el-select v-model="form.analysis_type" style="width: 100%">
                <el-option label="基本面分析" value="fundamental" />
                <el-option label="技术面分析" value="technical" />
                <el-option label="综合分析" value="comprehensive" />
              </el-select>
            </el-form-item>
            <el-form-item label="AI模型">
              <el-select v-model="form.model" style="width: 100%">
                <el-option label="DeepSeek" value="deepseek" />
                <el-option label="GPT-4" value="gpt4" />
                <el-option label="Claude" value="claude" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="startAnalysis" :loading="analyzing" style="width: 100%">
                <el-icon style="margin-right: 4px"><TrendCharts /></el-icon>
                开始分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="history-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>历史记录</span>
            </div>
          </template>
          <div class="history-list" v-loading="historyLoading">
            <div
              v-for="item in historyList"
              :key="item.id"
              class="history-item"
              @click="viewHistory(item)"
            >
              <div class="history-stock">{{ item.stock_code }} - {{ item.stock_name }}</div>
              <div class="history-type">{{ getTypeText(item.analysis_type) }}</div>
              <div class="history-time">{{ formatTime(item.created_at) }}</div>
            </div>
            <el-empty v-if="!historyLoading && historyList.length === 0" description="暂无历史记录" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>分析结果</span>
              <el-tag v-if="currentResult" :type="getSuggestionType(currentResult.suggestion)">
                {{ currentResult.suggestion || '待分析' }}
              </el-tag>
            </div>
          </template>
          <div v-if="!currentResult && !analyzing" class="empty-result">
            <el-empty description="请选择股票并开始分析" />
          </div>
          <div v-else-if="analyzing" class="analyzing">
            <el-icon class="is-loading" :size="48"><Loading /></el-icon>
            <p>AI正在分析中，请稍候...</p>
            <el-progress :percentage="50" :indeterminate="true" :duration="1" />
          </div>
          <div v-else class="result-content">
            <div v-if="currentResult.score" class="score-section">
              <div class="score-circle">
                <el-progress
                  type="circle"
                  :percentage="Math.round(currentResult.score)"
                  :color="getScoreColor(currentResult.score)"
                  :width="120"
                />
              </div>
              <div class="score-info">
                <div class="score-label">综合评分</div>
                <div class="score-value">{{ currentResult.score }}分</div>
              </div>
            </div>

            <el-divider v-if="currentResult.summary" />

            <div v-if="currentResult.summary" class="section">
              <h4>📊 分析摘要</h4>
              <div class="content-text">{{ currentResult.summary }}</div>
            </div>

            <div v-if="currentResult.fundamental" class="section">
              <h4>📈 基本面分析</h4>
              <div class="content-text">{{ currentResult.fundamental }}</div>
            </div>

            <div v-if="currentResult.technical" class="section">
              <h4>📉 技术面分析</h4>
              <div class="content-text">{{ currentResult.technical }}</div>
            </div>

            <div v-if="currentResult.risk" class="section">
              <h4>⚠️ 风险提示</h4>
              <div class="content-text risk">{{ currentResult.risk }}</div>
            </div>

            <div v-if="currentResult.suggestion" class="section">
              <h4>💡 操作建议</h4>
              <el-tag :type="getSuggestionType(currentResult.suggestion)" size="large">
                {{ currentResult.suggestion }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, Loading } from '@element-plus/icons-vue'
import request from '@/utils/request'

const analyzing = ref(false)
const historyLoading = ref(false)
const currentResult = ref(null)
const historyList = ref([])

const form = ref({
  stock_code: '',
  analysis_type: 'comprehensive',
  model: 'deepseek'
})

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getTypeText(type) {
  const map = {
    fundamental: '基本面',
    technical: '技术面',
    comprehensive: '综合'
  }
  return map[type] || type
}

function getScoreColor(score) {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

function getSuggestionType(suggestion) {
  const map = {
    '买入': 'success',
    '增持': 'success',
    '持有': 'warning',
    '减持': 'danger',
    '卖出': 'danger'
  }
  return map[suggestion] || ''
}

async function startAnalysis() {
  if (!form.value.stock_code) {
    ElMessage.warning('请输入股票代码')
    return
  }

  analyzing.value = true
  currentResult.value = null

  try {
    const res = await request({
      url: '/api/analysis/stock',
      method: 'post',
      data: {
        stock_code: form.value.stock_code,
        analysis_type: form.value.analysis_type,
        model: form.value.model
      }
    })

    if (res.code === 0) {
      currentResult.value = res.data
      ElMessage.success('分析完成')
      fetchHistory()
    } else {
      ElMessage.error(res.message || '分析失败')
      currentResult.value = {
        summary: '分析服务暂时不可用，请稍后再试。',
        suggestion: '待分析'
      }
    }
  } catch (error) {
    console.error('分析失败', error)
    ElMessage.error('分析失败，请检查网络连接')
    currentResult.value = {
      summary: '抱歉，分析过程中出现错误。请确保后端服务正常运行。',
      suggestion: '待分析'
    }
  } finally {
    analyzing.value = false
  }
}

function viewHistory(item) {
  currentResult.value = item
}

async function fetchHistory() {
  historyLoading.value = true
  try {
    const res = await request({
      url: '/api/analysis/history',
      method: 'get',
      params: { limit: 20 }
    })
    if (res.code === 0) {
      historyList.value = res.data || []
    }
  } catch (error) {
    console.error('获取历史记录失败', error)
  } finally {
    historyLoading.value = false
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.ai-analysis-container {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: #f5f7fa;
}

.history-item:last-child {
  border-bottom: none;
}

.history-stock {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.history-type {
  font-size: 12px;
  color: #666;
  margin-bottom: 2px;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.empty-result {
  padding: 60px 0;
}

.analyzing {
  text-align: center;
  padding: 60px 0;
}

.analyzing .el-icon {
  margin-bottom: 20px;
}

.analyzing p {
  color: #666;
  margin-bottom: 20px;
}

.result-content {
  padding: 10px 0;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 20px 0;
}

.score-circle {
  flex-shrink: 0;
}

.score-info {
  text-align: left;
}

.score-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.score-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
}

.section {
  margin-bottom: 24px;
}

.section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.content-text {
  line-height: 1.8;
  color: #666;
}

.content-text.risk {
  color: #e6a23c;
}
</style>
