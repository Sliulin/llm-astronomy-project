<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NResult, NButton, NSpace } from 'naive-ui'
import { HomeOutline, ArrowBackOutline } from '@vicons/ionicons5'

const router = useRouter()

function goHome() {
  router.push({ name: 'home' })
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="min-h-[calc(100vh-200px)] flex items-center justify-center">
    <NResult
      status="404"
      title="404 页面未找到"
      description="抱歉，您访问的页面不存在或已被移除"
    >
      <template #footer>
        <NSpace justify="center">
          <NButton @click="goBack">
            <template #icon>
              <NIcon><ArrowBackOutline /></NIcon>
            </template>
            返回上一页
          </NButton>
          <NButton type="primary" @click="goHome">
            <template #icon>
              <NIcon><HomeOutline /></NIcon>
            </template>
            返回首页
          </NButton>
        </NSpace>
      </template>
    </NResult>
  </div>
</template>
