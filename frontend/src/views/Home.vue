
<template>
  <div class="home-container">
    <div class="header">
      <h1>股票列表</h1>
      <div class="search-box">
        <el-input
          v-model="searchKey"
          placeholder="搜索股票代码/名称"
          style="width: 300px;"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>
    </div>

    <el-table :data="stockList" border style="width: 100%; margin-top: 20px;">
      <el-table-column prop="code" label="股票代码" width="120" />
      <el-table-column prop="name" label="股票名称" width="150" />
      <el-table-column prop="market" label="市场" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.market === 'SH' ? 'danger' : scope.row.market === 'SZ' ? 'success' : 'info'">
            {{ scope.row.market }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="industry" label="行业" width="150" />
      <el-table-column prop="listing_date" label="上市日期" width="120" />
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" type="primary" @click="handleAnalyze(scope.row)">AI分析</el-button>
          <el-button size="small" type="success" @click="handleAddFavorite(scope.row)">加自选</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-box" style="margin-top: 20px; text-align: right;">
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleQuery"
        @current-change="handleQuery"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getStockList } from '@/api/stock'

const searchKey = ref('')
const stockList = ref([])
const total = ref(0)
const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: ''
})

const handleQuery = async () => {
  queryParams.keyword = searchKey.value
  try {
    const res = await getStockList(queryParams)
    stockList.value = res.list
    total.value = res.total
  } catch (error) {
    console.error('获取股票列表失败', error)
  }
}

const handleSearch = () => {
  queryParams.page = 1
  handleQuery()
}

const handleAnalyze = (row) => {
  ElMessage.info(`AI分析 ${row.name} 功能开发中...`)
}

const handleAddFavorite = (row) => {
  ElMessage.success(`${row.name} 已添加到自选股`)
}

onMounted(() => {
  handleQuery()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header h1 {
  margin: 0;
  color: #333;
}
</style>
