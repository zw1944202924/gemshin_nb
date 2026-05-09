
import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/Layout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', noAuth: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', noAuth: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '股票列表' }
      },
      {
        path: 'ai-analysis',
        name: 'AIAnalysis',
        component: () => import('@/views/AIAnalysis.vue'),
        meta: { title: 'AI分析' }
      },
      {
        path: 'portfolio',
        name: 'Portfolio',
        component: () => import('@/views/Portfolio.vue'),
        meta: { title: '持仓管理' }
      },
      {
        path: 'favorite',
        name: 'Favorite',
        component: () => import('@/views/Favorite.vue'),
        meta: { title: '自选股' }
      },
      {
        path: 'quant',
        name: 'Quant',
        component: () => import('@/views/Quant.vue'),
        meta: { title: '量化选股' }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - AI股票分析助手` : 'AI股票分析助手'
  // 不需要登录的页面直接放行
  if (to.meta.noAuth) {
    next()
  } else {
    // 检查是否登录
    const token = localStorage.getItem('access_token')
    if (token) {
      next()
    } else {
      next('/login')
    }
  }
})

export default router
