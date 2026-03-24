<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import {
  NCard,
  NInput,
  NButton,
  NSpace,
  NList,
  NListItem,
  NIcon,
  NText,
  NTag,
  NEmpty,
  useMessage
} from 'naive-ui'
import {
  SendOutline,
  RefreshOutline,
  TrashOutline,
  PulseOutline,
  CodeWorkingOutline,
  EyeOutline,
  ChatbubbleOutline,
  PersonOutline,
  BulbOutline
} from '@vicons/ionicons5'
import { useSSE } from '@/composables/useSSE'
import type { SSEMessage } from '@/types'
import dayjs from 'dayjs'

const message = useMessage()

// SSE连接配置
const sseConfig = {
  url: '/api/sse',
  reconnectInterval: 3000,
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000
}

// 使用SSE组合式函数
const { connect, disconnect, reconnect, isConnected, messages, clearMessages, sendMessage } = useSSE(sseConfig)

// 输入消息
const inputMessage = ref('')
const messageContainer = ref<HTMLElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const isSending = ref(false)

// 消息类型配置
const messageTypeConfig: Record<string, { 
  label: string, 
  icon: any, 
  color: string,
  bgColor: string,
  tagType: 'default' | 'success' | 'info' | 'warning' | 'error' | 'primary'
}> = {
  connection: { 
    label: '连接', 
    icon: PulseOutline, 
    color: '#10b981', 
    bgColor: '#10b98120',
    tagType: 'success'
  },
  user: { 
    label: '用户', 
    icon: PersonOutline, 
    color: '#10b981', 
    bgColor: '#10b98120',
    tagType: 'success'
  },
  thinking: { 
    label: 'AI思考', 
    icon: BulbOutline, 
    color: '#3b82f6', 
    bgColor: '#3b82f620',
    tagType: 'info'
  },
  action: { 
    label: 'AI行动', 
    icon: CodeWorkingOutline, 
    color: '#3b82f6', 
    bgColor: '#3b82f620',
    tagType: 'info'
  },
  observation: { 
    label: 'AI观察', 
    icon: EyeOutline, 
    color: '#3b82f6', 
    bgColor: '#3b82f620',
    tagType: 'info'
  },
  answer: { 
    label: 'AI回答', 
    icon: ChatbubbleOutline, 
    color: '#3b82f6', 
    bgColor: '#3b82f620',
    tagType: 'info'
  }
}

// 过滤后的消息（排除心跳）
const displayMessages = computed(() => {
  return messages.value.filter(msg => msg.type !== 'heartbeat')
})

// 常规消息（用户消息、AI思考、AI回答）
const regularMessages = computed(() => {
  return displayMessages.value.filter(msg => 
    msg.type === 'question' || msg.type === 'thinking' || msg.type === 'answer'
  )
})

// AI行动和观察消息
const actionMessages = computed(() => {
  return displayMessages.value.filter(msg => 
    msg.type === 'action' || msg.type === 'observation'
  )
})

// 自动滚动到底部
async function scrollToBottom() {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    setTimeout(() => {
      if (messageContainer.value) {
        messageContainer.value.scrollTop = messageContainer.value.scrollHeight
      }
    }, 50)
  }
}

// 监听消息变化，自动滚动
watch(displayMessages, () => {
  scrollToBottom()
}, { deep: true })

// 组件挂载时连接
onMounted(() => {
  connect()
})

onUnmounted(() => {
  // 清理资源
})

// 发送消息
async function handleSend() {
  if (!inputMessage.value.trim()) {
    message.warning('请输入消息内容')
    return
  }

  if (!isConnected.value) {
    message.error('未连接到服务器，请检查连接状态')
    return
  }

  isSending.value = true
  const content = inputMessage.value.trim()

  try {
    // 添加用户消息
    const userMessage: SSEMessage = {
      id: crypto.randomUUID(),
      type: 'question',
      content: content,
      role: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    // 清空输入
    inputMessage.value = ''

    // 发送消息到服务器
    await sendMessage(content)

    message.success('消息已发送')
  } catch (error) {
    message.error('发送失败：' + (error as Error).message)
  } finally {
    isSending.value = false
  }
}

// 处理回车发送
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// 清空聊天记录
function handleClear() {
  clearMessages()
  message.success('聊天记录已清空')
}

// 格式化时间
function formatTime(date?: Date) {
  if (!date) return ''
  return dayjs(date).format('HH:mm:ss')
}

// 获取消息类型配置
function getMessageTypeConfig(type: string) {
  return messageTypeConfig[type] 
}
</script>

<template>
  <!-- 占满整个父容器 -->
  <div ref="containerRef" class="h-full flex flex-col overflow-hidden p-0 m-0" style="min-height: 0;">
    <!-- 工具栏 - 固定在顶部 -->
    <NCard class="flex-shrink-0 mb-4" size="small" :bordered="false">
      <NSpace justify="space-between" align="center">
        <NSpace align="center">
          <NTag :type="isConnected ? 'success' : 'error'" round>
            <template #icon>
              <NIcon>
                <PulseOutline />
              </NIcon>
            </template>
            {{ isConnected ? '已连接' : '未连接' }}
          </NTag>
          <NText depth="3">消息数: {{ displayMessages.length }}</NText>
        </NSpace>

        <NSpace>
          <NButton v-if="!isConnected" size="small" @click="reconnect">
            <template #icon>
              <NIcon><RefreshOutline /></NIcon>
            </template>
            重连
          </NButton>

          <NButton size="small" type="error" ghost @click="handleClear">
            <template #icon>
              <NIcon><TrashOutline /></NIcon>
            </template>
            清空
          </NButton>
        </NSpace>
      </NSpace>
    </NCard>

    <!-- 消息列表容器 - 占满剩余空间 -->
    <div class="flex-1 overflow-hidden min-h-0" style="flex: 1; min-height: 0;">
      <!-- 使用 grid 布局，5列网格，比例4:1 -->
      <div class="grid grid-cols-5 h-full gap-4 min-h-0">
        
        <!-- 常规消息栏 - 占4列 (80%) -->
        <NCard 
          class="col-span-4 min-w-0 h-full overflow-hidden"
          :bordered="false" 
          content-style="height: 100%; padding: 0; display: flex; flex-direction: column;"
        >
          <div
            ref="messageContainer"
            class="flex-1 overflow-y-auto p-4"
            style="min-height: 0;"
          >
            <!-- 无消息时显示空状态 -->
            <NEmpty 
              v-if="regularMessages.length === 0 && actionMessages.length === 0" 
              description="暂无消息，开始对话吧"
              class="h-full flex flex-col items-center justify-center"
            >
              <template #icon>
                <NIcon size="48" depth="3">
                  <ChatbubbleOutline />
                </NIcon>
              </template>
            </NEmpty>

            <!-- 有消息时正常显示列表 -->
            <NList v-else-if="regularMessages.length > 0" class="bg-transparent">
              <NListItem
                v-for="msg in regularMessages"
                :key="msg.id"
                class="!px-0 !py-3 animate-fade-in"
              >
                <div 
                  class="flex items-start gap-3" 
                  :class="{ 'flex-row-reverse': msg.role === 'user' }"
                >
                  <!-- 消息类型图标 -->
                  <div
                    class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                    :style="{ backgroundColor: getMessageTypeConfig(msg.type)?.bgColor || '#3b82f620' }"
                  >
                    <NIcon
                      :size="16"
                      :color="getMessageTypeConfig(msg.type)?.color || '#3b82f6'"
                    >
                      <component :is="getMessageTypeConfig(msg.type)?.icon || ChatbubbleOutline" /> 
                    </NIcon>
                  </div>

                  <!-- 消息内容 -->
                  <div class="flex-1 min-w-0">
                    <div 
                      class="flex items-center gap-2 mb-1 flex-wrap" 
                      :class="{ 'justify-end': msg.role === 'user' }"
                    >
                      <NTag
                        :type="getMessageTypeConfig(msg.type)?.tagType || 'primary'"
                        size="small"
                        round
                      >
                        {{ getMessageTypeConfig(msg.type)?.label || '消息' }}
                      </NTag>
                      <NText depth="3" class="text-xs">
                        {{ formatTime(msg.timestamp) }}
                      </NText>
                    </div>
                    
                    <div 
                      class="text-sm break-words whitespace-pre-line"
                      :style="{ 
                        color: getMessageTypeConfig(msg.type)?.color || '#3b82f6',
                        textAlign: msg.role === 'user' ? 'right' : 'left'
                      }"
                    >
                      {{ msg.content }}
                    </div>
                    
                    <!-- 附加数据 -->
                    <div 
                      v-if="msg.data" 
                      class="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs"
                      :class="{ 'text-right': msg.role === 'user' }"
                    >
                      <pre class="overflow-x-auto">{{ JSON.stringify(msg.data, null, 2) }}</pre>
                    </div>
                  </div>
                </div>
              </NListItem>
            </NList>
          </div>
        </NCard>

        <!-- AI行动和观察消息栏 - 占1列 (20%) -->
        <NCard 
          class="col-span-1 min-w-0 h-full overflow-hidden"
          :bordered="false" 
          content-style="height: 100%; padding: 0; display: flex; flex-direction: column;"
        >
          <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
            <NText strong>AI行动与观察</NText>
          </div>
          <div class="flex-1 overflow-y-auto p-4" style="min-height: 0;">
            <NList v-if="actionMessages.length > 0" class="bg-transparent">
              <NListItem
                v-for="msg in actionMessages"
                :key="msg.id"
                class="!px-0 !py-3 animate-fade-in"
              >
                <div class="flex items-start gap-3">
                  <!-- 消息类型图标 -->
                  <div
                    class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                    :style="{ backgroundColor: getMessageTypeConfig(msg.type)?.bgColor || '#3b82f620' }"
                  >
                    <NIcon
                      :size="16"
                      :color="getMessageTypeConfig(msg.type)?.color || '#3b82f6'"
                    >
                      <component :is="getMessageTypeConfig(msg.type)?.icon || ChatbubbleOutline" />
                    </NIcon>
                  </div>

                  <!-- 消息内容 -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1 flex-wrap">
                      <NTag
                        :type="getMessageTypeConfig(msg.type)?.tagType || 'primary'"
                        size="small"
                        round
                      >
                        {{ getMessageTypeConfig(msg.type)?.label || '消息' }}
                      </NTag>
                      <NText depth="3" class="text-xs">
                        {{ formatTime(msg.timestamp) }}
                      </NText>
                    </div>
                    
                    <div 
                      class="text-sm break-words whitespace-pre-line"
                      :style="{ 
                        color: getMessageTypeConfig(msg.type)?.color || '#3b82f6',
                      }"
                    >
                      {{ msg.content }}
                    </div>
                    
                    <!-- 附加数据 -->
                    <div 
                      v-if="msg.data" 
                      class="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs"
                    >
                      <pre class="overflow-x-auto">{{ JSON.stringify(msg.data, null, 2) }}</pre>
                    </div>
                  </div>
                </div>
              </NListItem>
            </NList>
            <NEmpty v-else description="暂无AI行动与观察消息" />
          </div>
        </NCard>
        
      </div>
    </div>

    <!-- 输入框 - 固定在底部 -->
    <NCard size="small" class="flex-shrink-0 mt-4" :bordered="false">
      <NSpace align="center" :size="12">
        <NInput
          v-model:value="inputMessage"
          type="textarea"
          placeholder="输入消息，按Enter发送，Shift+Enter换行..."
          :autosize="{ minRows: 2, maxRows: 6 }"
          class="flex-1"
          @keydown="handleKeydown"
          style="width: 1000px;"
        />
        <NButton
          type="primary"
          :disabled="!isConnected || !inputMessage.trim()"
          :loading="isSending"
          @click="handleSend"
        >
          <template #icon>
            <NIcon><SendOutline /></NIcon>
          </template>
          发送
        </NButton>
      </NSpace>
    </NCard>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.n-list-item) {
  border-bottom: 1px solid rgba(128, 128, 128, 0.1);
}

:deep(.n-list-item:last-child) {
  border-bottom: none;
}

:deep(.n-card__content) {
  height: 100%;
  overflow: hidden;
}

/* 确保空状态内容垂直居中 */
:deep(.n-empty) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 移除卡片边框，让界面更简洁 */
:deep(.n-card) {
  border: none;
}
</style>