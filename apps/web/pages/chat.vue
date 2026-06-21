<script setup lang="ts">
// 旧 /chat 路由已迁移到 /assistant，保留 query 参数直接跳转
const route = useRoute()
await navigateTo(`/assistant${route.fullPath.replace(/^\/chat/, "")}`, { replace: true })
</script>

<template>
  <div />
</template>
