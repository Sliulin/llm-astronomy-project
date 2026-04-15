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
             class="group relative w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors flex items-center justify-between"
             :class="activeSessionId === session.id ? 'bg-gray-800 text-gray-200 border border-gray-700' : 'text-gray-400 hover:bg-gray-900 hover:text-gray-300 border border-transparent'"
             @click="!editingSessionId && selectSession(session.id)">
          
          <template v-if="editingSessionId !== session.id">
            <span class="truncate flex-1 cursor-pointer">{{ session.title }}</span>
            <div class="opacity-0 group-hover:opacity-100 flex items-center ml-2 transition-opacity">
              <button @click.stop="startEdit(session)" class="p-1 text-gray-500 hover:text-blue-400 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
              </button>
              <button @click.stop="deleteSession(session.id)" class="p-1 text-gray-500 hover:text-red-400 transition-colors ml-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </div>
          </template>

          <template v-else>
            <input 
              :ref="(el) => { if (el) (el as HTMLInputElement).focus() }"
              v-model="editTitle" 
              @keyup.enter="saveEdit(session.id)"
              @keyup.esc="cancelEdit"
              @blur="saveEdit(session.id)"
              @click.stop
              class="flex-1 bg-gray-950 text-blue-300 border border-blue-500 rounded px-2 py-0.5 text-xs focus:outline-none w-full"
              placeholder="输入新任务名称..."
            />
          </template>
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
              {{ formatUserMessage(msg.content) }}
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
          <form 
            @submit.prevent="sendMessage" 
            @dragenter.prevent="isDragging = true"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            class="relative flex flex-col rounded-2xl border shadow-lg overflow-hidden transition-all duration-200"
            :class="isDragging ? 'border-blue-500 bg-gray-700 ring-2 ring-blue-500/50' : 'border-gray-700 bg-gray-800 focus-within:border-blue-500/50 focus-within:ring-1 focus-within:ring-blue-500/50'"
          >
            <div v-if="isDragging" class="pointer-events-none absolute inset-0 z-10 flex items-center justify-center bg-gray-800/90 backdrop-blur-sm border-2 border-dashed border-blue-500 rounded-2xl">
              <div class="flex items-center text-blue-400 font-medium">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                松开鼠标上传天文数据
              </div>
            </div>

            <div v-if="attachedFile" class="px-4 pt-3 pb-1 flex items-center relative z-0">
              <div class="flex items-center bg-gray-700/80 text-sm text-gray-200 px-3 py-1.5 rounded-lg border border-gray-600 shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
                <span class="truncate max-w-[200px]">{{ attachedFile.name }}</span>
                <button type="button" @click="removeAttachment" class="ml-3 text-gray-400 hover:text-red-400 transition-colors focus:outline-none">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
            </div>

            <div class="relative flex items-end w-full z-0">
              <div class="p-2 flex items-center justify-center">
                <input 
                  type="file" 
                  ref="fileInputRef" 
                  class="hidden" 
                  accept=".json,.csv,.txt,.fits" 
                  @change="handleFileUpload"
                />
                <button 
                  type="button"
                  @click="triggerUpload" 
                  :disabled="isUploading"
                  class="p-2 text-gray-400 hover:text-blue-400 transition-colors disabled:opacity-50 flex items-center justify-center h-10 w-10 rounded-xl hover:bg-gray-700"
                  title="上传本地数据文件"
                >
                  <svg v-if="!isUploading" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  <svg v-else class="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </button>
              </div>

              <textarea 
                v-model="userInput"
                @keydown.enter.prevent="handleEnter"
                placeholder="输入天文指令..." 
                class="flex-1 bg-transparent border-none py-4 px-2 text-gray-100 placeholder-gray-500 focus:outline-none resize-none max-h-48 min-h-[56px]"
                rows="1"
              ></textarea>

              <div class="p-2">
                <button type="submit" :disabled="!userInput.trim() || isSending" class="p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-xl transition-colors flex items-center justify-center h-10 w-10">
                  <svg v-if="!isSending" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" /></svg>
                  <span v-else class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></span>
                </button>
              </div>
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

const fileInputRef = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)
const attachedFile = ref<{ name: string, path: string } | null>(null)
const isDragging = ref(false)

const showJsonModal = ref(false)
const jsonPreviewHtml = ref('')

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
    const firstSession = sessions.value[0]
    if (firstSession) selectSession(firstSession.id)
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
  activeSessionId.value = '' 
  await fetchSessions()
}

const editingSessionId = ref<string | null>(null)
const editTitle = ref('')

const startEdit = (session: Session) => {
  editingSessionId.value = session.id
  editTitle.value = session.title
}

const cancelEdit = () => {
  editingSessionId.value = null
  editTitle.value = ''
}

const saveEdit = async (id: string) => {
  if (!editingSessionId.value) return 
  const newTitle = editTitle.value.trim()
  if (!newTitle) {
    cancelEdit()
    return
  }
  const sessionIndex = sessions.value.findIndex(s => s.id === id)
  if (sessionIndex !== -1) {
    const targetSession = sessions.value[sessionIndex]
    if (targetSession) targetSession.title = newTitle
  }
  editingSessionId.value = null
  try {
    await fetch(`http://localhost:8000/api/sessions/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTitle })
    })
  } catch (error) {
    console.error('更新标题失败:', error)
    fetchSessions()
  }
}

// ==============================
// 2. 通信逻辑
// ==============================
const connectSSE = () => {
  if (eventSource) eventSource.close()
  eventSource = new EventSource('http://localhost:8000/sse')
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'connection') return
      if (data.session_id && data.session_id !== activeSessionId.value) return
      const idx = messages.value.findIndex(m => m.id === data.id)
      if (idx !== -1) {
        messages.value[idx]!.content = data.content
      } else {
        messages.value.push(data)
      }
      if (data.type === 'answer' || data.type === 'error') {
        isSending.value = false
        fetchSessions() 
      }
    } catch (e) { console.error(e) }
  }
}

const sendMessage = async () => {
  let text = userInput.value.trim()
  if (!text || isSending.value) return
  const fullMessage = attachedFile.value ? `[本地文件路径: ${attachedFile.value.path}]\n${text}` : text
  messages.value.push({ id: Date.now().toString(), role: 'user', type: 'answer', content: fullMessage, timestamp: Date.now() })
  userInput.value = ''
  attachedFile.value = null 
  isSending.value = true
  try {
    await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: fullMessage, session_id: activeSessionId.value })
    })
  } catch (error) {
    messages.value.push({ id: Date.now().toString(), role: 'assistant', type: 'error', content: "网络请求失败" })
    isSending.value = false
  }
}

// ==============================
// 3. 文件上传逻辑
// ==============================
const triggerUpload = () => fileInputRef.value?.click()
const removeAttachment = () => attachedFile.value = null
const formatUserMessage = (content: string) => content.replace(/\[本地文件路径:\s*(?:.*?[\/\\])?([^\/\\\]]+)\]/g, '📎 $1')

const uploadFile = async (file: File) => {
  isUploading.value = true
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await fetch('http://localhost:8000/api/upload', { method: 'POST', body: formData })
    const data = await res.json()
    if (data.success) {
      attachedFile.value = { name: file.name, path: data.file_path }
    } else {
      alert(`上传失败: ${data.error}`)
    }
  } catch (error) {
    alert('上传请求失败。')
  } finally {
    isUploading.value = false
    if (fileInputRef.value) fileInputRef.value.value = ''
  }
}

const handleFileUpload = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) uploadFile(file)
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false 
  const file = e.dataTransfer?.files?.[0]
  if (file) {
    const validExts = ['.json', '.csv', '.txt', '.fits', '.gz']
    if (validExts.some(ext => file.name.toLowerCase().endsWith(ext))) {
      uploadFile(file)
    } else {
      alert('不支持的文件格式。')
    }
  }
}

// ==============================
// 4. JSON 预览逻辑
// ==============================
const openJsonPreview = async (url: string) => {
  try {
    const res = await fetch(url)
    const data = await res.json()
    let safeHtml = JSON.stringify(data, null, 2).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    safeHtml = safeHtml.replace(/(https?:\/\/[^\s",]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300 underline font-bold">$1</a>')
    jsonPreviewHtml.value = safeHtml
    showJsonModal.value = true
  } catch (error) {
    window.open(url, '_blank')
  }
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) sendMessage()
}

onMounted(() => { fetchSessions(); connectSSE() })
onUnmounted(() => eventSource?.close())
</script>

<style scoped>
textarea::-webkit-scrollbar { width: 6px; }
textarea::-webkit-scrollbar-track { background: transparent; }
textarea::-webkit-scrollbar-thumb { background-color: #374151; border-radius: 20px; }
</style>