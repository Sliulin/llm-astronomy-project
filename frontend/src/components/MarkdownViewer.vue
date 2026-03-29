<template>
  <div 
    class="markdown-renderer text-gray-200 leading-relaxed max-w-none" 
    v-html="renderedContent"
    @click="handleLinkClick"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItKatex from 'markdown-it-katex'
import 'katex/dist/katex.min.css'

const props = defineProps<{
  content: string
}>()

// ==========================================
// 【新增逻辑】：定义 emit 事件并拦截点击
// ==========================================
const emit = defineEmits<{
  (e: 'preview-json', url: string): void
}>()

const handleLinkClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  const aTag = target.closest('a')
  
  // 如果点击的是本地的 json 下载链接，拦截它！
  if (aTag && aTag.href.includes('/downloads/') && aTag.href.endsWith('.json')) {
    e.preventDefault() // 阻止浏览器打开新标签页
    emit('preview-json', aTag.href) // 通知父组件打开弹窗
  }
}
// ==========================================

// 初始化 Markdown 解析器
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  typographer: true
}).use(markdownItKatex)

// 拦截并重写 <a> 标签，强制在新标签页打开 (TypeScript 安全版)
const defaultRender = md.renderer.rules.link_open

md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  const token = tokens[idx]
  
  if (token) {
    token.attrSet('target', '_blank')
    token.attrSet('rel', 'noopener noreferrer')
  }
  
  if (defaultRender) {
    return defaultRender(tokens, idx, options, env, self)
  } else {
    return self.renderToken(tokens, idx, options)
  }
}

// 渲染前预处理：防止大模型吐出原始 Python 字典导致的渲染失败
const preprocessContent = (text: string) => {
  if (!text) return ''
  
  if (text.trim().startsWith('{') && text.includes("'links'")) {
    return '```json\n' + text + '\n```'
  }
  
  return text.replace(/\[([^\]]+)\]\s+\((https?:\/\/[^\s)]+)\)/g, '[$1]($2)')
}

const renderedContent = computed(() => {
  const safeContent = preprocessContent(props.content)
  return md.render(safeContent)
})
</script>

<style>
/* 核心：解决链接不可见问题 */
.markdown-renderer a {
  color: #60a5fa !important;
  text-decoration: underline !important;
  font-weight: 600;
  transition: color 0.2s;
  word-break: break-all;
}

.markdown-renderer a:hover {
  color: #93c5fd !important;
  text-decoration: none !important;
}

/* 针对 FITS/GZ 下载链接增加小图标提示 */
.markdown-renderer a[href$=".gz"]::before,
.markdown-renderer a[href$=".fits"]::before,
.markdown-renderer a[href*="/downloads/"]::before {
  content: "📥 ";
  text-decoration: none;
  display: inline-block;
}

/* 表格样式美化 */
.markdown-renderer table {
  display: table;
  width: 100%;
  table-layout: auto;
  border-collapse: separate;
  border-spacing: 0;
  margin: 1.25rem 0;
  border: 1px solid #374151;
  border-radius: 8px;
  overflow: hidden;
}

.markdown-renderer th,
.markdown-renderer td {
  padding: 0.75rem;
  border-bottom: 1px solid #374151;
  text-align: center;
  vertical-align: middle;
}

.markdown-renderer th:first-child,
.markdown-renderer td:first-child {
  width: 100px; 
  word-break: break-word; 
}

.markdown-renderer th {
  background-color: #1f2937;
  color: #f3f4f6;
  font-weight: 600;
}

.markdown-renderer td {
  color: #d1d5db;
}

.markdown-renderer tr:last-child td {
  border-bottom: none;
}

.markdown-renderer tr:nth-child(even) td {
  background-color: rgba(55, 65, 81, 0.3);
}

.katex-display {
  margin: 1rem 0;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-renderer p {
  margin-bottom: 1rem;
}
</style>