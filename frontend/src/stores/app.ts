import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SSEMessage, ConnectionStatus } from '@/types'

export const useAppStore = defineStore('app', () => {
  // State
  const messages = ref<SSEMessage[]>([])
  const connectionStatus = ref<ConnectionStatus>('disconnected')
  const lastHeartbeat = ref<Date | null>(null)
  const reconnectAttempts = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isConnected = computed(() => connectionStatus.value === 'connected')
  const hasError = computed(() => error.value !== null)
  const messageCount = computed(() => messages.value.length)

  // Actions
  function addMessage(message: SSEMessage) {
    messages.value.push({
      ...message,
      timestamp: new Date()
    })
    // 限制消息数量，最多保留100条
    if (messages.value.length > 100) {
      messages.value = messages.value.slice(-100)
    }
  }

  function clearMessages() {
    messages.value = []
  }

  function setConnectionStatus(status: ConnectionStatus) {
    connectionStatus.value = status
  }

  function updateHeartbeat() {
    lastHeartbeat.value = new Date()
  }

  function incrementReconnectAttempts() {
    reconnectAttempts.value++
  }

  function resetReconnectAttempts() {
    reconnectAttempts.value = 0
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  function setError(err: string | null) {
    error.value = err
  }

  function clearError() {
    error.value = null
  }

  function updateMessage(updatedMessage: SSEMessage) {
    const index = messages.value.findIndex(msg => msg.id === updatedMessage.id)
    if (index !== -1) {
      // 创建一个新对象，确保触发Vue的响应式更新
      messages.value[index] = { ...updatedMessage }
    }
  }

  return {
    // State
    messages,
    connectionStatus,
    lastHeartbeat,
    reconnectAttempts,
    isLoading,
    error,
    // Getters
    isConnected,
    hasError,
    messageCount,
    // Actions
    addMessage,
    updateMessage,
    clearMessages,
    setConnectionStatus,
    updateHeartbeat,
    incrementReconnectAttempts,
    resetReconnectAttempts,
    setLoading,
    setError,
    clearError
  }
})
