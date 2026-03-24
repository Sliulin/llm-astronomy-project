<script setup lang="ts">
import {
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NSpace,
  NText,
  NH1,
  NH2,
  NDivider,
  NTag,
  NTimeline,
  NTimelineItem,
  NIcon
} from 'naive-ui'
import {
  RocketOutline,
  CodeOutline,
  SparklesOutline,
  GitBranchOutline
} from '@vicons/ionicons5'

// 版本历史
const versions = [
  {
    version: 'v1.0.0',
    date: '2025-03-10',
    title: '初始版本',
    content: '项目初始化，实现基础功能'
  }
]

// 开发团队
const team = [
  { name: '前端开发', role: 'Vue 3 + TypeScript', color: 'success' },
  { name: '后端开发', role: 'Python + FastAPI', color: 'info' },
  { name: 'AI模型', role: '腾讯混元大模型', color: 'warning' }
]
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <NH1 class="text-center mb-8">关于 AI Agent</NH1>

    <!-- 项目介绍 -->
    <NCard class="mb-6">
      <template #header>
        <NSpace align="center">
          <NIcon size="24" color="#3b82f6">
            <RocketOutline />
          </NIcon>
          <span class="text-lg font-semibold">项目简介</span>
        </NSpace>
      </template>

      <NText class="text-base leading-relaxed">
        AI Agent 是一个基于大语言模型的智能助手系统，采用现代化的前后端技术栈构建。
        系统支持实时流式对话、工具调用、多轮上下文理解等功能，为用户提供智能化的交互体验。
      </NText>

      <NDivider />

      <NDescriptions label-placement="left" :column="2">
        <NDescriptionsItem label="项目名称">AI Agent 智能助手</NDescriptionsItem>
        <NDescriptionsItem label="当前版本">v1.0.0</NDescriptionsItem>
        <NDescriptionsItem label="开源协议">MIT License</NDescriptionsItem>
        <NDescriptionsItem label="支持语言">中文、英文</NDescriptionsItem>
      </NDescriptions>
    </NCard>

    <!-- 技术架构 -->
    <NCard class="mb-6">
      <template #header>
        <NSpace align="center">
          <NIcon size="24" color="#8b5cf6">
            <CodeOutline />
          </NIcon>
          <span class="text-lg font-semibold">技术架构</span>
        </NSpace>
      </template>

      <NH3 class="mb-4">前端技术栈</NH3>
      <NSpace :size="8" wrap class="mb-6">
        <NTag type="success">Vue 3.5+</NTag>
        <NTag type="success">TypeScript 5.9+</NTag>
        <NTag type="success">Vite 6+</NTag>
        <NTag type="info">Vue Router 5+</NTag>
        <NTag type="info">Pinia 3+</NTag>
        <NTag type="warning">Naive UI 2.44+</NTag>
        <NTag type="warning">TailwindCSS 4.2+</NTag>
        <NTag type="error">@vueuse/core</NTag>
      </NSpace>

      <NH3 class="mb-4">后端技术栈</NH3>
      <NSpace :size="8" wrap class="mb-6">
        <NTag type="success">Python 3.9+</NTag>
        <NTag type="success">FastAPI</NTag>
        <NTag type="info">OpenAI API</NTag>
        <NTag type="warning">腾讯混元大模型</NTag>
      </NSpace>

      <NH3 class="mb-4">通信协议</NH3>
      <NSpace :size="8" wrap>
        <NTag type="success">Server-Sent Events (SSE)</NTag>
        <NTag type="info">WebSocket</NTag>
        <NTag type="warning">RESTful API</NTag>
      </NSpace>
    </NCard>

    <!-- 核心特性 -->
    <NCard class="mb-6">
      <template #header>
        <NSpace align="center">
          <NIcon size="24" color="#10b981">
            <SparklesOutline />
          </NIcon>
          <span class="text-lg font-semibold">核心特性</span>
        </NSpace>
      </template>

      <NSpace vertical :size="16">
        <div>
          <NH4>🚀 实时流式响应</NH4>
          <NText depth="2">
            采用Server-Sent Events技术实现大模型的流式输出，用户可以实时看到AI的思考过程和回复内容。
          </NText>
        </div>

        <div>
          <NH4>🛠️ 工具调用能力</NH4>
          <NText depth="2">
            支持动态工具注册和调用，AI可以根据用户需求自动选择合适的工具完成任务。
          </NText>
        </div>

        <div>
          <NH4>💬 多轮对话支持</NH4>
          <NText depth="2">
            维护对话上下文，支持多轮连续对话，提供连贯的交互体验。
          </NText>
        </div>

        <div>
          <NH4>📱 响应式设计</NH4>
          <NText depth="2">
            采用TailwindCSS实现响应式布局，完美适配桌面端和移动端设备。
          </NText>
        </div>

        <div>
          <NH4>🔒 稳定可靠</NH4>
          <NText depth="2">
            实现心跳检测和自动重连机制，确保连接稳定性；支持错误处理和异常恢复。
          </NText>
        </div>
      </NSpace>
    </NCard>

    <!-- 版本历史 -->
    <NCard class="mb-6">
      <template #header>
        <NSpace align="center">
          <NIcon size="24" color="#f59e0b">
            <GitBranchOutline />
          </NIcon>
          <span class="text-lg font-semibold">版本历史</span>
        </NSpace>
      </template>

      <NTimeline>
        <NTimelineItem
          v-for="version in versions"
          :key="version.version"
          :type="version.version === 'v1.0.0' ? 'success' : 'default'"
          :title="version.title"
          :content="version.content"
          :time="version.date"
        >
          <template #header>
            <NTag type="success" size="small">{{ version.version }}</NTag>
          </template>
        </NTimelineItem>
      </NTimeline>
    </NCard>

    <!-- 开发团队 -->
    <NCard>
      <template #header>
        <span class="text-lg font-semibold">开发团队</span>
      </template>

      <NSpace :size="16" wrap>
        <NCard
          v-for="member in team"
          :key="member.name"
          size="small"
          class="w-48"
        >
          <NSpace vertical align="center">
            <NTag :type="member.color as any" round size="large">
              {{ member.name }}
            </NTag>
            <NText depth="2">{{ member.role }}</NText>
          </NSpace>
        </NCard>
      </NSpace>
    </NCard>
  </div>
</template>
