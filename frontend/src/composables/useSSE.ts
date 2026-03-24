import { ref, computed, onUnmounted, watch } from 'vue'
import { useEventSource } from '@vueuse/core'
import { useIntervalFn } from '@vueuse/core'
import type { SSEMessage, SSEConfig, ConnectionStatus } from '@/types'
import { useAppStore } from '@/stores/app'

export function useSSE(config: SSEConfig) {
  const appStore = useAppStore()

  // 配置默认值
  const {
    url,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    withCredentials = false
  } = config

  // 状态
  const eventSource = ref<EventSource | null>(null)
  const connectionStatus = ref<ConnectionStatus>('disconnected')
  const messages = ref<SSEMessage[]>([])
  const lastHeartbeat = ref<Date | null>(null)
  const reconnectAttempts = ref(0)
  const error = ref<Error | null>(null)
  const connectionId = ref<string>('') // 存储连接ID

  // 计算属性
  const isConnected = computed(() => connectionStatus.value === 'connected')
  const canReconnect = computed(() => reconnectAttempts.value < maxReconnectAttempts)

  // 自定义EventSource创建函数，用于获取连接ID
  function createEventSource(url: string) {
    const es = new EventSource(url)
    
    // 监听open事件，尝试获取连接ID
    es.addEventListener('open', (event) => {
      // 注意：由于EventSource API的限制，无法直接获取响应头
      // 这里我们需要通过其他方式获取连接ID
      // 实际实现中，服务器会在首次消息中包含连接ID
    })
    
    return es
  }

  // 使用 vueuse 的 useEventSource
  const { status, data, error: esError, close, open } = useEventSource(url, [], {
    autoReconnect: {
      retries: maxReconnectAttempts,
      delay: reconnectInterval,
      onFailed() {
        connectionStatus.value = 'error'
        appStore.setConnectionStatus('error')
      }
    },
    immediate: false,
    withCredentials
  })

  // 心跳检测
  const { pause: pauseHeartbeat, resume: resumeHeartbeat } = useIntervalFn(
    () => {
      if (isConnected.value) {
        // 检查最后心跳时间
        if (lastHeartbeat.value) {
          const timeSinceLastHeartbeat = Date.now() - lastHeartbeat.value.getTime()
          if (timeSinceLastHeartbeat > heartbeatInterval * 2) {
            // 心跳超时，重新连接
            console.warn('Heartbeat timeout, reconnecting...')
            reconnect()
            return
          }
        }

        // 发送心跳消息
        const heartbeatMessage: SSEMessage = {
          type: 'heartbeat',
          content: 'ping',
          timestamp: new Date()
        }
        messages.value.push(heartbeatMessage)
        lastHeartbeat.value = new Date()
        appStore.updateHeartbeat()
      }
    },
    heartbeatInterval,
    { immediate: false }
  )

  // 解析SSE消息
  function parseMessage(data: string): SSEMessage | null {
    try {
      // 尝试解析JSON
      const parsed = JSON.parse(data)

      // 类型守卫
      if (typeof parsed === 'object' && parsed !== null) {
        // 验证必需字段
        if ('type' in parsed && 'content' in parsed) {
          // 如果消息包含连接ID，保存它
          if (parsed.connectionId) {
            connectionId.value = parsed.connectionId
          }
          
          return {
            id: parsed.id || crypto.randomUUID(),
            type: parsed.type as SSEMessage['type'],
            content: String(parsed.content),
            role: parsed.role,
            data: parsed.data,
            timestamp: new Date(),
            is_append: parsed.is_append
          }
        }

        // 心跳消息特殊处理
        if (parsed.type === 'heartbeat') {
          return {
            type: 'heartbeat',
            content: 'pong',
            timestamp: new Date()
          }
        }
      }

      // 如果不是JSON，作为普通消息处理
      return {
        id: crypto.randomUUID(),
        type: 'message',
        content: data,
        timestamp: new Date()
      }
    } catch {
      // JSON解析失败，作为普通文本消息
      return {
        id: crypto.randomUUID(),
        type: 'message',
        content: data,
        timestamp: new Date()
      }
    }
  }

  // 监听数据变化
  watch(data, (newData) => {
    if (newData) {
      const message = parseMessage(newData)
      if (message) {
        // 处理追加消息
        if (message.is_append && message.id) {
          const existingMessageIndex = messages.value.findIndex(msg => msg.id === message.id)
          if (existingMessageIndex !== -1) {
            // 更新现有消息的内容
            const existingMessage = messages.value[existingMessageIndex]
            if (existingMessage) {
              // 创建一个新对象，确保触发Vue的响应式更新
              const updatedMessage = {
                ...existingMessage,
                content: existingMessage.content + message.content
              }
              messages.value[existingMessageIndex] = updatedMessage
              appStore.updateMessage(updatedMessage)
            }
          } else {
            // 如果找不到对应ID的消息，作为新消息添加
            messages.value.push(message)
            appStore.addMessage(message)
          }
        } else {
          // 普通消息，直接添加
          messages.value.push(message)
          appStore.addMessage(message)
        }

        // 更新心跳时间
        if (message.type === 'heartbeat') {
          lastHeartbeat.value = new Date()
          appStore.updateHeartbeat()
        }
      }
    }
  })

  // 监听状态变化
  watch(status, (newStatus) => {
    if (newStatus === 'OPEN') {
      connectionStatus.value = 'connected'
      appStore.setConnectionStatus('connected')
      appStore.resetReconnectAttempts()
      reconnectAttempts.value = 0
      error.value = null
      resumeHeartbeat()
    } else if (newStatus === 'CLOSED') {
      connectionStatus.value = 'disconnected'
      appStore.setConnectionStatus('disconnected')
      pauseHeartbeat()
    } else if (newStatus === 'CONNECTING') {
      connectionStatus.value = 'connecting'
      appStore.setConnectionStatus('connecting')
    }
  })

  // 监听错误
  watch(esError, (newError) => {
    if (newError) {
      const errorMessage = newError instanceof Error ? newError.message : String(newError)
      error.value = newError instanceof Error ? newError : new Error(errorMessage)
      connectionStatus.value = 'error'
      appStore.setConnectionStatus('error')
      appStore.setError(errorMessage)
      pauseHeartbeat()
    }
  })

  // 连接方法
  function connect() {
    if (connectionStatus.value === 'connected') {
      console.warn('Already connected')
      return
    }

    connectionStatus.value = 'connecting'
    appStore.setConnectionStatus('connecting')
    open()
  }

  // 断开连接
  function disconnect() {
    close()
    pauseHeartbeat()
    connectionStatus.value = 'disconnected'
    appStore.setConnectionStatus('disconnected')
    eventSource.value = null
    connectionId.value = '' // 清空连接ID
  }

  // 重新连接
  function reconnect() {
    if (!canReconnect.value) {
      console.error('Max reconnection attempts reached')
      connectionStatus.value = 'error'
      appStore.setConnectionStatus('error')
      return
    }

    connectionStatus.value = 'reconnecting'
    appStore.setConnectionStatus('reconnecting')
    reconnectAttempts.value++
    appStore.incrementReconnectAttempts()

    disconnect()

    // 延迟重新连接
    setTimeout(() => {
      connect()
    }, reconnectInterval)
  }

  // 发送消息（通过HTTP POST）
  async function sendMessage(content: string, data?: Record<string, unknown>): Promise<void> {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: content,
          type: 'question',
          role: 'user',
          data,
          connectionId: connectionId.value, // 包含连接ID
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      console.error('Failed to send message:', errorMessage)
      throw err
    }
  }

  // 清空消息
  function clearMessages() {
    messages.value = []
    appStore.clearMessages()
  }

  // 组件卸载时清理
  onUnmounted(() => {
    disconnect()
  })

  return {
    // 状态
    connectionStatus,
    messages,
    lastHeartbeat,
    reconnectAttempts,
    error,
    connectionId,
    // 计算属性
    isConnected,
    canReconnect,
    // 方法
    connect,
    disconnect,
    reconnect,
    sendMessage,
    clearMessages
  }
}
