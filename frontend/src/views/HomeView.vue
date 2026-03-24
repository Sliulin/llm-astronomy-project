<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NButton,
  NSpace,
  NGrid,
  NGridItem,
  NIcon,
  NText,
  NH1,
  NH2,
  NDescriptions,
  NDescriptionsItem,
  NTag,
  NDivider
} from 'naive-ui'
import {
  ChatbubbleOutline,
  FlashOutline,
  ShieldCheckmarkOutline,
  GlobeOutline,
  ArrowForwardOutline
} from '@vicons/ionicons5'

const router = useRouter()

// 功能特性
const features = [
  {
    icon: ChatbubbleOutline,
    title: '智能对话',
    description: '基于大语言模型的自然语言交互，支持多轮对话和上下文理解',
    color: '#3b82f6'
  },
  {
    icon: FlashOutline,
    title: '实时响应',
    description: '采用SSE技术实现流式输出，响应速度快，体验流畅',
    color: '#8b5cf6'
  },
  {
    icon: ShieldCheckmarkOutline,
    title: '安全可靠',
    description: '数据加密传输，支持心跳检测和自动重连机制',
    color: '#10b981'
  },
  {
    icon: GlobeOutline,
    title: '跨平台支持',
    description: '响应式设计，完美适配桌面端和移动端设备',
    color: '#f59e0b'
  }
]

// 技术栈
const techStack = [
  { name: 'Vue 3', version: '3.5+', type: 'success' },
  { name: 'Vite', version: '6.0+', type: 'success' },
  { name: 'TypeScript', version: '5.9+', type: 'info' },
  { name: 'Naive UI', version: '2.44+', type: 'warning' },
  { name: 'TailwindCSS', version: '4.2+', type: 'primary' },
  { name: 'Pinia', version: '3.0+', type: 'success' }
]

// 跳转到对话页面
function goToChat() {
  router.push({ name: 'chat' })
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <!-- Hero Section -->
    <div class="text-center py-16 md:py-24">
      <NH1 class="text-4xl md:text-6xl font-bold mb-6">
        <span class="bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
          AI Agent
        </span>
        智能助手
      </NH1>
      <NText class="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto block mb-8">
        基于先进的AI技术，提供智能对话、实时数据处理和自动化任务执行能力
      </NText>
      <NSpace justify="center" :size="16">
        <NButton type="primary" size="large" @click="goToChat">
          <template #icon>
            <NIcon><ChatbubbleOutline /></NIcon>
          </template>
          开始对话
        </NButton>
        <NButton size="large" @click="$router.push({ name: 'about' })">
          了解更多
        </NButton>
      </NSpace>
    </div>

    <!-- 功能特性 -->
    <div class="py-12">
      <NH2 class="text-center mb-12">核心功能</NH2>
      <NGrid :cols="4" :x-gap="24" :y-gap="24" responsive="screen">
        <NGridItem v-for="feature in features" :key="feature.title" :span="4" md:span="2" lg:span="1">
          <NCard hoverable class="h-full">
            <div class="text-center">
              <div
                class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                :style="{ backgroundColor: feature.color + '20' }"
              >
                <NIcon :size="32" :color="feature.color">
                  <component :is="feature.icon" />
                </NIcon>
              </div>
              <h3 class="text-lg font-semibold mb-2">{{ feature.title }}</h3>
              <NText class="text-gray-600 dark:text-gray-400">
                {{ feature.description }}
              </NText>
            </div>
          </NCard>
        </NGridItem>
      </NGrid>
    </div>

    <NDivider />

    <!-- 技术栈 -->
    <div class="py-12">
      <NH2 class="text-center mb-8">技术栈</NH2>
      <NSpace justify="center" :size="12" wrap>
        <NTag
          v-for="tech in techStack"
          :key="tech.name"
          :type="tech.type as any"
          size="large"
          round
        >
          {{ tech.name }} {{ tech.version }}
        </NTag>
      </NSpace>
    </div>

    <!-- 系统信息 -->
    <div class="py-12">
      <NCard title="系统信息">
        <NDescriptions label-placement="left" bordered :column="2">
          <NDescriptionsItem label="前端框架">Vue 3 + TypeScript</NDescriptionsItem>
          <NDescriptionsItem label="构建工具">Vite 6</NDescriptionsItem>
          <NDescriptionsItem label="UI组件库">Naive UI</NDescriptionsItem>
          <NDescriptionsItem label="样式方案">TailwindCSS 4</NDescriptionsItem>
          <NDescriptionsItem label="状态管理">Pinia</NDescriptionsItem>
          <NDescriptionsItem label="路由管理">Vue Router 5</NDescriptionsItem>
          <NDescriptionsItem label="实时通信">Server-Sent Events (SSE)</NDescriptionsItem>
          <NDescriptionsItem label="部署平台">Netlify</NDescriptionsItem>
        </NDescriptions>
      </NCard>
    </div>
  </div>
</template>

<style scoped>
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.from-blue-500 {
  --tw-gradient-from: #3b82f6;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(59, 130, 246, 0));
}

.to-purple-600 {
  --tw-gradient-to: #8b5cf6;
}

.bg-clip-text {
  -webkit-background-clip: text;
  background-clip: text;
}
</style>
