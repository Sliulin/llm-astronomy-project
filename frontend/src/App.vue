<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { NConfigProvider, NMessageProvider, zhCN, dateZhCN, darkTheme, lightTheme } from 'naive-ui'
import { useOsTheme } from 'naive-ui'
import AppLayout from '@/layouts/AppLayout.vue'

const route = useRoute()
const osTheme = useOsTheme()

// 根据系统主题自动切换
const theme = computed(() => (osTheme.value === 'dark' ? darkTheme : lightTheme))

// 是否需要显示布局
const showLayout = computed(() => {
  return !route.meta.hideLayout
})
</script>

<template>
  <NConfigProvider
    :theme="theme"
    :locale="zhCN"
    :date-locale="dateZhCN"
    :breakpoints="{ xs: 0, s: 640, m: 768, l: 1024, xl: 1280, xxl: 1536 }"
  >
    <NMessageProvider>
      <AppLayout v-if="showLayout">
        <RouterView v-slot="{ Component }">
          <KeepAlive :include="['HomeView', 'ChatView']">
            <component :is="Component" />
          </KeepAlive>
        </RouterView>
      </AppLayout>
      <RouterView v-else />
    </NMessageProvider>
  </NConfigProvider>
</template>

<style scoped>
/* 全局过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
