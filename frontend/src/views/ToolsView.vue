<template>
  <div class="flex-1 overflow-y-auto bg-gray-950 text-gray-100 p-6 md:p-10 relative">
    <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/5 rounded-full blur-[100px] pointer-events-none"></div>
    
    <div class="max-w-7xl mx-auto relative z-10">
      <div class="mb-12">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-4">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          Registry Status: Online
        </div>
        <h1 class="text-4xl font-extrabold tracking-tight mb-4">工具库 <span class="text-gray-500 font-light">/ Tools Registry</span></h1>
        <p class="text-lg text-gray-400 max-w-3xl leading-relaxed">
          AstroAgent 在后台可以自主调用的所有天文 API 接口。当您在观测台中输入自然语言指令时，大语言模型会自动从下方工具库中选择合适的工具进行数据检索。
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="tool in tools" 
          :key="tool.name" 
          class="bg-gray-900 border border-gray-800 rounded-2xl p-6 hover:-translate-y-1 hover:border-blue-500/50 hover:shadow-[0_10px_30px_-15px_rgba(59,130,246,0.3)] transition-all duration-300 group flex flex-col"
        >
          <div class="flex justify-between items-start mb-5">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-gray-800 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform group-hover:bg-blue-500/10">
                <span v-html="tool.icon"></span>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-200 group-hover:text-blue-400 transition-colors">{{ tool.name }}</h3>
                <span class="text-xs font-medium px-2 py-0.5 rounded-md bg-gray-800 text-gray-400 border border-gray-700">
                  {{ tool.category }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1.5 text-xs text-green-500 bg-green-500/10 px-2 py-1 rounded border border-green-500/20">
              <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span>
              Active
            </div>
          </div>

          <p class="text-sm text-gray-400 leading-relaxed mb-6 flex-1">
            {{ tool.description }}
          </p>

          <div class="mt-auto">
            <div class="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              Parameters Schema
            </div>
            <div class="bg-gray-950 rounded-lg p-3 overflow-x-auto border border-gray-800/50">
              <pre class="text-xs font-mono text-gray-300 m-0 whitespace-pre-wrap leading-relaxed">{{ tool.params }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 1. 定义响应式变量
const tools = ref<any[]>([])
const isLoading = ref(true)

// 2. SVG 图标库保持不变
const icons = {
  search: `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>`,
  database: `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>`,
  image: `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>`,
  wave: `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>`,
  map: `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg>`
}

// 3. 智能匹配系统：根据后端传来的工具名称，自动分配 UI 分类和图标
const getUIConfig = (toolName: string) => {
  const name = toolName.toLowerCase()
  if (name.includes('image')) return { category: '图像检索', icon: icons.image }
  if (name.includes('spectra')) return { category: '光谱分析', icon: icons.wave }
  if (name.includes('adql')) return { category: '高阶查询', icon: icons.database }
  if (name.includes('region') || name.includes('coord')) return { category: '范围查询', icon: icons.map }
  return { category: '基础查询', icon: icons.search }
}

// 4. 生命周期钩子：页面加载时向后端请求数据
onMounted(async () => {
  try {
    isLoading.value = true
    const res = await fetch('http://localhost:8000/api/tools')
    const backendTools = await res.json()
    
    // 将后端原始数据与前端 UI 结合
    tools.value = backendTools.map((t: any) => ({
      ...t,
      ...getUIConfig(t.name)
    }))
  } catch (error) {
    console.error("加载工具列表失败:", error)
    // 降级处理：如果你没开后端，显示一个错误卡片
    tools.value = [{
      name: 'Network_Error',
      description: '无法连接到 AstroAgent 后端服务，请检查 server.py 是否正在运行。',
      params: '{ "status": "offline" }',
      category: '系统异常',
      icon: icons.database
    }]
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
/* 隐藏代码块的滚动条，保持美观 */
pre::-webkit-scrollbar {
  height: 6px;
}
pre::-webkit-scrollbar-track {
  background: transparent;
}
pre::-webkit-scrollbar-thumb {
  background-color: #374151;
  border-radius: 10px;
}
</style>