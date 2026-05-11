
<template>
  <div class="layout-container">
    <el-container style="height: 100vh; border: 1px solid #eee;">
      <el-aside width="200px" style="background-color: rgb(238, 241, 246);">
        <el-menu :default-active="activeMenu" router class="el-menu-vertical-demo">
          <el-menu-item index="/home">
            <el-icon><Grid /></el-icon>
            <span>股票列表</span>
          </el-menu-item>
          <el-menu-item index="/ai-analysis">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI分析</span>
          </el-menu-item>
          <el-menu-item index="/portfolio">
            <el-icon><Wallet /></el-icon>
            <span>持仓管理</span>
          </el-menu-item>
          <el-menu-item index="/favorite">
            <el-icon><Star /></el-icon>
            <span>自选股</span>
          </el-menu-item>
          <el-menu-item index="/quant">
            <el-icon><TrendCharts /></el-icon>
            <span>量化选股</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header style="text-align: right; font-size: 12px; background: #fff; border-bottom: 1px solid #eee;">
          <div style="display: flex; align-items: center; justify-content: flex-end; height: 100%;">
            <span style="margin-right: 20px;">欢迎，{{ userInfo?.username || '用户' }}</span>
            <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Grid, ChatDotRound, Wallet, Star, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const activeMenu = computed(() => route.path)
const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || '{}'))

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_info')
  ElMessage.success('退出登录成功')
  router.push('/login')
}
</script>

<style scoped>
.el-header {
  padding: 0 20px;
}
.el-menu-item {
  font-size: 14px;
}
</style>
