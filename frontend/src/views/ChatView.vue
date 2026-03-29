<template>
  <div class="absolute inset-0 flex bg-gray-900 text-gray-100">
    <aside class="w-64 border-r border-gray-800 bg-gray-950/50 flex flex-col hidden md:flex h-full">
      <div class="p-4">
        <button @click="createNewSession" class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors border border-gray-700 hover:border-gray-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          新建观测任务
        </button>
      </div>
      <div class="flex-1 overflow-y-auto px-3 space-y-1">
        <div class="text-xs font-semibold text-gray-500 px-3 py-2 uppercase tracking-wider">历史记录</div>
        
        <div v-for="session in sessions" :key="session.id" 
             class="group relative w-full text-left px-3 py-2.5 rounded-lg text-sm truncate transition-colors cursor-pointer flex items-center justify-between"
             :class="activeSessionId === session.id ? 'bg-gray-800 text-gray-200 border border-gray-700' : 'text-gray-400 hover:bg-gray-900 hover:text-gray-300 border border-transparent'"
             @click="selectSession(session.id)">
          <span class="truncate flex-1">{{ session.title }}</span>
          
          <button @click.stop="deleteSession(session.id)" class="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 transition-opacity ml-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
          </button>
        </div>
      </div>
    </aside>

    <section class="flex-1 flex flex-col relative h-full">
      <div class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6" ref="chatContainer">
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400 space-y-4">
          <div class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" /></svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-200">AstroAgent 已就绪</h2>
        </div>

        <div v-for="msg in messages" :key="msg.id" class="max-w-4xl mx-auto flex gap-4" :class="{'flex-row-reverse': msg.role === 'user'}">
          <div class="flex-shrink-0 mt-1">
            <div v-if="msg.role === 'user'" class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-sm font-bold">U</div>
            <div v-else class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" /></svg>
            </div>
          </div>
          
          <div class="flex-1 max-w-[85%]" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
            <div v-if="msg.role === 'user'" class="inline-block bg-gray-800 border border-gray-700 rounded-2xl px-5 py-3 text-gray-100 whitespace-pre-wrap text-left">
              {{ msg.content }}
            </div>
            
            <div v-else class="inline-block w-full">
              <div v-if="['thinking', 'action', 'observation'].includes(msg.type)" class="text-sm text-gray-400 mb-2 flex items-center gap-2 bg-gray-800/50 p-3 rounded-xl border border-gray-700/50 w-fit">
                <span v-if="msg.type === 'thinking'" class="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></span>
                <svg v-else-if="msg.type === 'action'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                {{ msg.content }}
              </div>
              <div v-else-if="msg.type === 'answer'" class="w-full">
                <MarkdownViewer :content="msg.content" @preview-json="openJsonPreview"/>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="p-4 bg-gray-900 border-t border-gray-800">
        <div class="max-w-4xl mx-auto relative">
          <form @submit.prevent="sendMessage" class="relative flex items-end bg-gray-800 rounded-2xl border border-gray-700 shadow-lg overflow-hidden focus-within:border-blue-500/50 focus-within:ring-1 focus-within:ring-blue-500/50 transition-all">
            <textarea 
              v-model="userInput"
              @keydown.enter.prevent="handleEnter"
              placeholder="输入天文指令..." 
              class="flex-1 bg-transparent border-none py-4 px-5 text-gray-100 placeholder-gray-500 focus:outline-none resize-none max-h-48 min-h-[56px]"
              rows="1"
            ></textarea>
            <div class="p-2">
              <button type="submit" :disabled="!userInput.trim() || isSending" class="p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-xl transition-colors flex items-center justify-center h-10 w-10">
                <svg v-if="!isSending" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" /></svg>
                <span v-else class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
    <div v-if="showJsonModal" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/80 backdrop-blur-sm p-4 sm:p-6" @click.self="showJsonModal = false">
      <div class="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-4xl flex flex-col max-h-[85vh] overflow-hidden transform transition-all">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-900/50">
          <h3 class="text-gray-200 font-bold flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
            天文数据原始视图
          </h3>
          <button @click="showJsonModal = false" class="text-gray-500 hover:text-red-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto bg-gray-950 flex-1 custom-scrollbar">
          <pre class="text-green-400 font-mono text-sm leading-relaxed whitespace-pre-wrap break-all" v-html="jsonPreviewHtml"></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import MarkdownViewer from '@/components/MarkdownViewer.vue'

interface Session { id: string; title: string; updated_at: number }
interface Message { id: string; role: 'user' | 'assistant' | 'system'; type: string; content: string; timestamp?: number; session_id?: string }

const userInput = ref('')
const messages = ref<Message[]>([])
const sessions = ref<Session[]>([])
const activeSessionId = ref('')
const isSending = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
let eventSource: EventSource | null = null

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

watch(messages, () => { scrollToBottom() }, { deep: true })

// ==============================
// 1. 会话管理逻辑
// ==============================
const fetchSessions = async () => {
  const res = await fetch('http://localhost:8000/api/sessions')
  sessions.value = await res.json()
  
  if (sessions.value.length > 0 && !activeSessionId.value) {
    // 【修复报错】先安全地取出第一个元素
    const firstSession = sessions.value[0]
    // 明确判断它存在后，再读取它的 id
    if (firstSession) {
      selectSession(firstSession.id)
    }
  }
}

const selectSession = async (id: string) => {
  activeSessionId.value = id
  const res = await fetch(`http://localhost:8000/api/sessions/${id}`)
  messages.value = await res.json()
  scrollToBottom()
}

const createNewSession = async () => {
  const res = await fetch('http://localhost:8000/api/sessions', { method: 'POST' })
  const data = await res.json()
  await fetchSessions()
  selectSession(data.id)
}

const deleteSession = async (id: string) => {
  await fetch('http://localhost:8000/api/sessions/' + id, { method: 'DELETE' })
  activeSessionId.value = '' // 清空选中状态，强制重新拉取
  await fetchSessions()
}

// ==============================
// 2. 核心通信逻辑
// ==============================
const connectSSE = () => {
  if (eventSource) eventSource.close()
  eventSource = new EventSource('http://localhost:8000/sse')
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'connection') return
      
      // 【关键防御】防止后台流式消息串台到其他会话界面
      if (data.session_id && data.session_id !== activeSessionId.value) return

      const existingMsgIndex = messages.value.findIndex(m => m.id === data.id)
      if (existingMsgIndex !== -1) {
        messages.value[existingMsgIndex]!.content = data.content
      } else {
        messages.value.push(data)
      }
      
      
      if (data.type === 'answer' || data.type === 'error') {
        isSending.value = false
        // 对话结束后刷新侧边栏，更新标题
        fetchSessions() 
      }
    } catch (e) { console.error(e) }
  }
}

const sendMessage = async () => {
  const text = userInput.value.trim()
  if (!text || isSending.value) return

  // 前端立刻上屏
  messages.value.push({
    id: Date.now().toString(),
    role: 'user',
    type: 'answer',
    content: text,
    timestamp: Date.now()
  })
  userInput.value = ''
  isSending.value = true

  // 附带 session_id 发送给后端
  try {
    await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: activeSessionId.value })
    })
  } catch (error) {
    messages.value.push({ id: Date.now().toString(), role: 'assistant', type: 'error', content: "网络请求失败" })
    isSending.value = false
  }
}

// --- JSON 预览模态框逻辑 ---
const showJsonModal = ref(false)
const jsonPreviewHtml = ref('') // 注意：这里改名为了 Html

const openJsonPreview = async (url: string) => {
  try {
    const res = await fetch(url)
    const data = await res.json()
    
    // 1. 先转成带缩进的字符串
    const jsonString = JSON.stringify(data, null, 2)
    
    // 2. 将字符串中的 HTML 特殊字符转义（防止 XSS 攻击或数据中有 < > 导致渲染错乱）
    let safeHtml = jsonString
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      
    // 3. 正则匹配：识别所有的 http/https 链接，并用 <a> 标签包裹起来
    const urlRegex = /(https?:\/\/[^\s",]+)/g
    safeHtml = safeHtml.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300 underline font-bold transition-colors">$1</a>')
    
    jsonPreviewHtml.value = safeHtml
    showJsonModal.value = true
  } catch (error) {
    console.error('获取JSON数据失败:', error)
    window.open(url, '_blank')
  }
}

const handleEnter = (e: KeyboardEvent) => {
  if (e.shiftKey) return
  sendMessage()
}

onMounted(() => {
  fetchSessions()
  connectSSE()
})

onUnmounted(() => {
  if (eventSource) eventSource.close()
})
</script>

<style scoped>
textarea::-webkit-scrollbar { width: 6px; }
textarea::-webkit-scrollbar-track { background: transparent; }
textarea::-webkit-scrollbar-thumb { background-color: #374151; border-radius: 20px; }
</style>