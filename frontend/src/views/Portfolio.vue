<<<<<<< HEAD

<template>
  <div class="page-container">
    <h2>持仓管理</h2>
    <el-alert title="功能开发中..." type="info" style="margin-top: 20px;" />
=======
<template>
  <div class="portfolio-container">
    <div class="header">
      <h2>持仓管理</h2>
      <div class="header-right">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon style="margin-right: 4px;"><Plus /></el-icon>
          添加持仓
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="summary-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-item">
            <div class="label">持仓市值</div>
            <div class="value">{{ formatPrice(summary.totalValue) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-item">
            <div class="label">持仓成本</div>
            <div class="value">{{ formatPrice(summary.totalCost) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-item">
            <div class="label">持仓收益</div>
            <div class="value" :class="getPriceClass(summary.profit)">
              {{ formatPrice(summary.profit) }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-item">
            <div class="label">收益率</div>
            <div class="value" :class="getPriceClass(summary.profitRate)">
              {{ formatChange(summary.profitRate) }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="content">
      <el-table
        :data="portfolioList"
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
        <el-table-column label="持仓数量" width="100">
          <template #default="scope">
            {{ scope.row.quantity }}
          </template>
        </el-table-column>
        <el-table-column label="成本价" width="100">
          <template #default="scope">
            {{ formatPrice(scope.row.cost_price) }}
          </template>
        </el-table-column>
        <el-table-column label="现价" width="100">
          <template #default="scope">
            <span :class="getPriceClass(scope.row.change_rate)">
              {{ formatPrice(scope.row.current_price) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="市值" width="120">
          <template #default="scope">
            {{ formatPrice(scope.row.market_value) }}
          </template>
        </el-table-column>
        <el-table-column label="持仓收益" width="120">
          <template #default="scope">
            <span :class="getPriceClass(scope.row.profit)">
              {{ formatPrice(scope.row.profit) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="收益率" width="100" sortable prop="profit_rate">
          <template #default="scope">
            <span :class="getPriceClass(scope.row.profit_rate)">
              {{ formatChange(scope.row.profit_rate) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="success" link @click="handleAnalyze(scope.row)">分析</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && portfolioList.length === 0" description="暂无持仓记录" />
    </div>

    <el-dialog v-model="showAddDialog" :title="editMode ? '编辑持仓' : '添加持仓'" width="450px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="股票代码" prop="stock_code">
          <el-input v-model="form.stock_code" placeholder="如: 000001" :disabled="editMode" />
        </el-form-item>
        <el-form-item label="股票名称" prop="stock_name">
          <el-input v-model="form.stock_name" placeholder="如: 平安银行" />
        </el-form-item>
        <el-form-item label="持仓数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="成本价" prop="cost_price">
          <el-input-number v-model="form.cost_price" :min="0" :precision="2" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getPortfolioList, createPortfolio, updatePortfolio, deletePortfolio } from '@/api/portfolio'

const loading = ref(false)
const submitLoading = ref(false)
const showAddDialog = ref(false)
const editMode = ref(false)
const editId = ref(null)
const portfolioList = ref([])
const formRef = ref(null)

const form = ref({
  stock_code: '',
  stock_name: '',
  quantity: 100,
  cost_price: 0
})

const rules = {
  stock_code: [{ required: true, message: '请输入股票代码', trigger: 'blur' }],
  stock_name: [{ required: true, message: '请输入股票名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入持仓数量', trigger: 'blur' }],
  cost_price: [{ required: true, message: '请输入成本价', trigger: 'blur' }]
}

const summary = computed(() => {
  let totalValue = 0
  let totalCost = 0
  let totalProfit = 0

  portfolioList.value.forEach(item => {
    const marketValue = (item.quantity || 0) * (item.current_price || item.cost_price || 0)
    const cost = (item.quantity || 0) * (item.cost_price || 0)
    const profit = marketValue - cost

    totalValue += marketValue
    totalCost += cost
    totalProfit += profit
  })

  const profitRate = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0

  return {
    totalValue,
    totalCost,
    profit: totalProfit,
    profitRate
  }
})

function formatPrice(price) {
  if (!price && price !== 0) return '-'
  return '¥' + Number(price).toFixed(2)
}

function formatChange(rate) {
  if (!rate && rate !== 0) return '-'
  return (rate > 0 ? '+' : '') + Number(rate).toFixed(2) + '%'
}

function getPriceClass(rate) {
  if (!rate || rate === 0) return ''
  return rate > 0 ? 'price-up' : 'price-down'
}

async function fetchPortfolio() {
  loading.value = true
  try {
    const res = await getPortfolioList()
    if (res.code === 0) {
      portfolioList.value = (res.data || []).map(item => ({
        ...item,
        current_price: item.current_price || item.cost_price,
        market_value: (item.quantity || 0) * (item.current_price || item.cost_price || 0),
        profit: ((item.current_price || item.cost_price || 0) - (item.cost_price || 0)) * (item.quantity || 0),
        profit_rate: item.cost_price ? (((item.current_price || item.cost_price) - item.cost_price) / item.cost_price) * 100 : 0
      }))
    }
  } catch (error) {
    console.error('获取持仓列表失败', error)
  } finally {
    loading.value = false
  }
}

function handleEdit(row) {
  editMode.value = true
  editId.value = row.id
  form.value = {
    stock_code: row.stock_code,
    stock_name: row.stock_name,
    quantity: row.quantity,
    cost_price: row.cost_price
  }
  showAddDialog.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除 ${row.stock_name} 的持仓记录吗？`, '提示', {
      type: 'warning'
    })
    await deletePortfolio(row.id)
    ElMessage.success('删除成功')
    fetchPortfolio()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleAnalyze(row) {
  ElMessage.info('分析功能开发中...')
}

function handleClose() {
  showAddDialog.value = false
  editMode.value = false
  editId.value = null
  form.value = {
    stock_code: '',
    stock_name: '',
    quantity: 100,
    cost_price: 0
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (editMode.value) {
          await updatePortfolio(editId.value, form.value)
          ElMessage.success('更新成功')
        } else {
          await createPortfolio(form.value)
          ElMessage.success('添加成功')
        }
        handleClose()
        fetchPortfolio()
      } catch (error) {
        ElMessage.error(editMode.value ? '更新失败' : '添加失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchPortfolio()
})
</script>

<style scoped>
.portfolio-container {
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
  font-size: 20px;
  font-weight: 600;
}

.summary-cards {
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: 600;
}

.stock-code {
  font-weight: 500;
  color: #409eff;
}

.price-up {
  color: #f56c6c;
}

.price-down {
  color: #67c23a;
}
</style>
>>>>>>> feature/backend-api-enhancement
