<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NLayout,
  NLayoutSider,
  NLayoutHeader,
  NLayoutContent,
  NMenu,
  NButton,
  NIcon,
  NBadge,
  NTooltip,
  NDropdown,
  NAvatar,
  NSpace,
  NText
} from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  HomeOutline,
  ChatbubbleOutline,
  InformationCircleOutline,
  MenuOutline,
  SunnyOutline,
  MoonOutline,
  PersonCircleOutline,
  SettingsOutline,
  LogOutOutline
} from '@vicons/ionicons5'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

// 侧边栏折叠状态
const collapsed = ref(false)

// 当前选中菜单
const activeKey = computed(() => route.name as string)

// 菜单配置
const menuOptions: MenuOption[] = [
  {
    label: '首页',
    key: 'home',
    icon: () => h(NIcon, null, { default: () => h(HomeOutline) })
  },
  {
    label: '智能对话',
    key: 'chat',
    icon: () => h(NIcon, null, { default: () => h(ChatbubbleOutline) }),
    badge: () => h(NBadge, { value: appStore.messageCount, max: 99 })
  },
  {
    label: '关于',
    key: 'about',
    icon: () => h(NIcon, null, { default: () => h(InformationCircleOutline) })
  }
]

// 用户下拉菜单
const userOptions = [
  {
    label: '个人设置',
    key: 'settings',
    icon: () => h(NIcon, null, { default: () => h(SettingsOutline) })
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(NIcon, null, { default: () => h(LogOutOutline) })
  }
]

// 处理菜单选择
function handleMenuSelect(key: string) {
  router.push({ name: key })
}

// 处理用户菜单选择
function handleUserSelect(key: string) {
  if (key === 'logout') {
    // 处理退出登录
    console.log('Logout')
  } else if (key === 'settings') {
    // 处理设置
    console.log('Settings')
  }
}

// 切换侧边栏
function toggleSider() {
  collapsed.value = !collapsed.value
}
</script>

<template>
  <!-- 最外层 - 移除 n-layout-scroll-container，改为 flex 布局 -->
  <div class="h-screen flex overflow-hidden">
    <!-- 侧边栏 -->
    <div class="hidden md:block w-64 border-r">
      <div class="h-16 flex items-center justify-center border-b">
        <NSpace align="center" :size="8">
          <NIcon size="28" class="text-primary">
            <ChatbubbleOutline />
          </NIcon>
          <NText strong class="text-lg">AI Agent</NText>
        </NSpace>
      </div>

      <NMenu
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
        class="mt-4"
      />
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- 顶部导航 -->
      <NLayoutHeader bordered class="h-16 px-4 flex items-center justify-between flex-shrink-0">
        <NSpace align="center">
          <NButton quaternary circle class="md:hidden" @click="toggleSider">
            <template #icon>
              <NIcon><MenuOutline /></NIcon>
            </template>
          </NButton>
          <span class="text-lg font-medium">{{ route.meta.title || 'AI Agent' }}</span>
        </NSpace>

        <NSpace align="center" :size="16">
          <!-- 连接状态指示器 -->
          <NTooltip>
            <template #trigger>
              <div
                class="w-3 h-3 rounded-full"
                :class="{
                  'bg-success': appStore.isConnected,
                  'bg-warning': appStore.connectionStatus === 'connecting',
                  'bg-danger': appStore.connectionStatus === 'error'
                }"
              />
            </template>
            <span>
              {{ 
                appStore.isConnected 
                  ? '已连接' 
                  : appStore.connectionStatus === 'connecting' 
                    ? '连接中...' 
                    : '连接错误'
              }}
            </span>
          </NTooltip>

          <!-- 用户菜单 -->
          <NDropdown :options="userOptions" @select="handleUserSelect">
            <NButton quaternary circle>
              <template #icon>
                <NAvatar
                  size="small"
                  :style="{ backgroundColor: '#3b82f6' }"
                >
                  <NIcon><PersonCircleOutline /></NIcon>
                </NAvatar>
              </template>
            </NButton>
          </NDropdown>
        </NSpace>
      </NLayoutHeader>

      <!-- 内容区 -->
      <div 
        class="flex-1 overflow-hidden p-4"
        style="min-height: 0;"
      >
        <!-- 移除内部的 n-layout-scroll-container，直接放置组件 -->
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 侧边栏样式 */
:deep(.n-menu) {
  height: calc(100vh - 64px);
  overflow-y: auto;
}
</style>
