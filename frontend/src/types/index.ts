// SSE消息类型
export interface SSEMessage {
  id?: string
  type: 'question' | 'thinking' | 'action' | 'observation' | 'answer' | 'heartbeat' | 'connection' | 'error' | 'message'
  content: string
  data?: Record<string, unknown>
  timestamp?: Date
  role?: 'user' | 'assistant' | 'system'
  is_append?: boolean
}

// 连接状态
export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'reconnecting' | 'error'

// SSE配置
export interface SSEConfig {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
  withCredentials?: boolean
}

// 心跳消息
export interface HeartbeatMessage {
  type: 'heartbeat'
  timestamp: number
}

// 工具调用
export interface ToolCall {
  name: string
  parameters: Record<string, unknown>
}

// 代理响应
export interface AgentResponse {
  type: 'thinking' | 'action' | 'observation' | 'answer'
  content: string
  toolCall?: ToolCall
}

// 用户消息
export interface UserMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
}

// 聊天会话
export interface ChatSession {
  id: string
  title: string
  messages: UserMessage[]
  createdAt: Date
  updatedAt: Date
}
