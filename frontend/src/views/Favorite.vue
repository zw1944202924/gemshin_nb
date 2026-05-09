<<<<<<< HEAD

<template>
  <div class="page-container">
    <h2>自选股</h2>
    <el-alert title="功能开发中..." type="info" style="margin-top: 20px;" />
=======
<template>
  <div class="favorite-container">
    <div class="header">
      <h2>我的关注</h2>
      <div class="header-right">
        <el-input
          v-model="searchKey"
          placeholder="搜索股票代码/名称"
          style="width: 200px; margin-right: 12px;"
          clearable
          @clear="handleQuery"
          @keyup.enter="handleQuery"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="sortType" style="width: 140px; margin-right: 12px;" @change="handleSort">
          <el-option label="按添加时间" value="time" />
          <el-option label="按涨跌幅" value="change" />
          <el-option label="按最新价" value="price" />
        </el-select>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon style="margin-right: 4px;"><Plus /></el-icon>
          添加股票
        </el-button>
      </div>
    </div>

    <div class="content">
      <el-table
        :data="filteredList"
        border
        style="width: 100%;"
        :header-cell-style="{ background: '#f5f7fa', color: '#333' }"
        v-loading="loading"
      >
        <el-table-column prop="stock_code" label="股票代码" width="120">
          <template #default="scope">
            <span class="stock-code">{{ scope.row.stock_code }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock_name" label="股票名称" width="150" />
        <el-table-column label="最新价" width="120" sortable prop="latest_price">
          <template #default="scope">
            <span :class="getPriceClass(scope.row.change_rate)">
              {{ formatPrice(scope.row.latest_price) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="涨跌幅" width="120" sortable prop="change_rate">
          <template #default="scope">
            <span :class="getPriceClass(scope.row.change_rate)">
              {{ formatChange(scope.row.change_rate) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="关注时间" width="180" sortable prop="created_at">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleAnalyze(scope.row)">分析</el-button>
            <el-button size="small" type="danger" link @click="handleRemove(scope.row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && watchlist.length === 0" description="暂无关注股票" />
    </div>

    <el-dialog v-model="showAddDialog" title="添加关注股票" width="400px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="股票代码">
          <el-input v-model="addForm.stock_code" placeholder="如: 000001" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="addLoading">添加</el-button>
      </template>
    </el-dialog>
>>>>>>> feature/backend-api-enhancement
  </div>
</template>

<script setup>
<<<<<<< HEAD
</script>

<style scoped>
.page-container {
  padding: 20px;
}
</style>
=======
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getWatchlist, addToWatchlist, removeFromWatchlist } from '@/api/watchlist'

const loading = ref(false)
const addLoading = ref(false)
const showAddDialog = ref(false)
const searchKey = ref('')
const sortType = ref('time')
const watchlist = ref([])
const addForm = ref({ stock_code: '' })

let refreshTimer = null

const getUserId = () => {
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    return JSON.parse(userInfo).id || 1
  }
  return 1
}

const fetchWatchlist = async () => {
  loading.value = true
  try {
    const res = await getWatchlist({ user_id: getUserId() })
    watchlist.value = res || []
  } catch (error) {
    console.error('获取关注列表失败', error)
  } finally {
    loading.value = false
  }
}

const filteredList = computed(() => {
  let list = [...watchlist.value]
  if (searchKey.value) {
    const key = searchKey.value.toLowerCase()
    list = list.filter(item => 
      item.stock_code.toLowerCase().includes(key) ||
      item.stock_name.toLowerCase().includes(key)
    )
  }
  return list
})

const handleSort = () => {
  const list = [...watchlist.value]
  switch (sortType.value) {
    case 'change':
      watchlist.value = list.sort((a, b) => b.change_rate - a.change_rate)
      break
    case 'price':
      watchlist.value = list.sort((a, b) => b.latest_price - a.latest_price)
      break
    default:
      watchlist.value = list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
}

const handleQuery = () => {
  fetchWatchlist()
}

const handleAdd = async () => {
  if (!addForm.value.stock_code) {
    ElMessage.warning('请输入股票代码')
    return
  }
  addLoading.value = true
  try {
    await addToWatchlist({ 
      stock_code: addForm.value.stock_code, 
      user_id: getUserId() 
    })
    ElMessage.success('添加成功')
    showAddDialog.value = false
    addForm.value.stock_code = ''
    fetchWatchlist()
  } catch (error) {
    console.error('添加失败', error)
  } finally {
    addLoading.value = false
  }
}

const handleRemove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定取消关注 ${row.stock_name} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await removeFromWatchlist({ 
      watchlist_id: row.id, 
      user_id: getUserId() 
    })
    ElMessage.success('取消关注成功')
    fetchWatchlist()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消关注失败', error)
    }
  }
}

const handleAnalyze = (row) => {
  ElMessage.info(`AI分析 ${row.stock_name} 功能开发中...`)
}

const formatPrice = (price) => {
  return price ? price.toFixed(2) : '0.00'
}

const formatChange = (rate) => {
  if (rate === null || rate === undefined) return '0.00%'
  return (rate > 0 ? '+' : '') + rate.toFixed(2) + '%'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const getPriceClass = (rate) => {
  if (rate > 0) return 'price-up'
  if (rate < 0) return 'price-down'
  return 'price-normal'
}

onMounted(() => {
  fetchWatchlist()
  refreshTimer = setInterval(fetchWatchlist, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.favorite-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.content {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.stock-code {
  color: #409eff;
  font-weight: 500;
}

.price-up {
  color: #f56c6c;
  font-weight: 500;
}

.price-down {
  color: #67c23a;
  font-weight: 500;
}

.price-normal {
  color: #909399;
}
</style>
>>>>>>> feature/backend-api-enhancement
