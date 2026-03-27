<template>
  <div class="flex-1 flex flex-col items-center justify-center p-6 relative">
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>

    <div class="text-center z-10 max-w-3xl">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-6 shadow-[0_0_20px_rgba(59,130,246,0.15)]">
        <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
        v0.1.0 · LLM Astronomy Engine
      </div>
      
      <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
        探索宇宙的<br/>
        <span class="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">智能数据引擎</span>
      </h1>
      
      <p class="text-lg text-gray-400 mb-10 leading-relaxed max-w-2xl mx-auto">
        接入最新天文学数据库，通过自然语言查询星表、分析光谱、检索深空图像。由大语言模型驱动，专为科研人员与天文爱好者打造。
      </p>

      <div class="flex justify-center gap-4">
        <button @click="$router.push('/chat')" class="px-8 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium transition-all shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:shadow-[0_0_30px_rgba(59,130,246,0.6)] hover:-translate-y-0.5">
          启动观测 (Chat)
        </button>
        <button @click="$router.push('/tools')" class="px-8 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-600 text-white font-medium transition-all">
          查看工具库
        </button>
      </div>
    </div>
  </div>
</template>