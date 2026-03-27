<template>
  <div class="min-h-screen bg-gray-950 text-gray-100 font-sans selection:bg-blue-500/30 flex flex-col">
    <header class="sticky top-0 z-50 border-b border-gray-800 bg-gray-950/80 backdrop-blur-md">
      <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]">
            A
          </div>
          <span class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 tracking-wide">
            AstroAgent
          </span>
        </div>
        
        <nav class="flex gap-6">
          <RouterLink to="/" class="text-gray-400 hover:text-white transition-colors py-2 px-1 border-b-2 border-transparent hover:border-blue-500" active-class="text-white border-blue-500">主页</RouterLink>
          <RouterLink to="/chat" class="text-gray-400 hover:text-white transition-colors py-2 px-1 border-b-2 border-transparent hover:border-blue-500" active-class="text-white border-blue-500">观测台</RouterLink>
          <RouterLink to="/tools" class="text-gray-400 hover:text-white transition-colors py-2 px-1 border-b-2 border-transparent hover:border-blue-500" active-class="text-white border-blue-500">工具箱</RouterLink>
        </nav>
      </div>
    </header>

    <main class="flex-1 flex flex-col relative overflow-hidden">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style>
/* 确保滚动条暗黑风格 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #030712; 
}
::-webkit-scrollbar-thumb {
  background: #374151; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #4b5563; 
}
</style>