<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-10">
      <h1 class="text-3xl font-bold text-white flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
        </svg>
        系统工具箱
      </h1>
      <p class="mt-2 text-gray-400">以下是 AstroAgent 当前支持的所有可用工具，大模型会根据您的需求自动调用它们。</p>
    </div>

    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>

    <div v-else>
      <div v-for="(toolList, categoryName) in groupedTools" :key="categoryName" class="mb-12">
        
        <div class="flex items-center gap-3 mb-6 border-b border-gray-800 pb-3">
          <span class="w-1.5 h-6 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.6)]"></span>
          <h2 class="text-2xl font-bold text-gray-200 tracking-wide">{{ categoryName }}</h2>
          <span class="px-2.5 py-0.5 rounded-full bg-gray-800 text-gray-400 text-sm font-medium border border-gray-700 ml-2">
            {{ toolList.length }} 个工具
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="tool in toolList" :key="tool.name" 
               class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-[0_0_20px_rgba(59,130,246,0.15)] transition-all duration-300 group flex flex-col">
            
            <div class="flex items-start gap-4 mb-4">
              <div class="p-3 bg-gray-800 rounded-lg group-hover:bg-blue-900/30 transition-colors">
                <span class="text-2xl">{{ tool.icon || '🔧' }}</span>
              </div>
              <div>
                <h3 class="text-lg font-bold text-white mb-1">{{ tool.title || tool.name }}</h3>
                <code class="text-xs text-blue-400 bg-blue-900/20 px-2 py-1 rounded">{{ tool.name }}</code>
              </div>
            </div>
            
            <p class="text-gray-400 text-sm leading-relaxed mb-4 h-16 line-clamp-3">
              {{ tool.description }}
            </p>
            
            <div class="bg-gray-950 rounded-lg p-3 border border-gray-800 w-full">
              <div class="text-xs font-semibold text-gray-500 mb-2">接收参数 (JSON Schema)</div>
              <pre class="text-xs text-green-400 font-mono overflow-y-auto overflow-x-auto max-h-48 custom-scrollbar">{{ formatParams(tool.parameters) }}</pre>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const isLoading = ref(true)
const tools = ref<any[]>([])

// 挂载时从后端 API 获取动态注册的工具集
onMounted(async () => {
  try {
    isLoading.value = true
    const res = await fetch('http://localhost:8000/api/tools')
    
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const backendTools = await res.json()
    
    tools.value = backendTools.map((t: any) => ({
      ...t,
    }))
  } catch (error) {
    console.error("加载工具列表失败:", error)
    // 后端离线时的降级展示
    tools.value = [{
      name: 'Backend_Offline',
      description: '无法连接到后端服务。请检查 Python 后端是否已启动 (python start-all.py)。',
      parameters: { properties: { status: { type: "string" } } },
      title: '后端离线',
      icon: '❌',
      category: '⚠️ 系统异常'
    }]
  } finally {
    isLoading.value = false
  }
})

//根据后端返回的 category 标签对工具进行分组
const groupedTools = computed(() => {
  const groups: Record<string, any[]> = {}

  tools.value.forEach(tool => {
    const cat = tool.category || '📦 其他系统工具'
    if (!groups[cat]) {
      groups[cat] = []
    }
    groups[cat].push(tool)
  })

  return groups
})

//格式化 JSON 参数以便于阅读
const formatParams = (params: any) => {
  if (!params || !params.properties) return '{}'
  return JSON.stringify(params.properties, null, 2)
}
</script>

<style scoped>
/* 自定义滚动条美化 */
.custom-scrollbar::-webkit-scrollbar {
  height: 6px;
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(17, 24, 39, 0.5);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(55, 65, 81, 0.8);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(75, 85, 99, 1);
}

/* 限制描述文字行数 */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}
</style>