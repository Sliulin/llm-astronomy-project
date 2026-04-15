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
// 事件定义与点击拦截
// ==========================================
const emit = defineEmits<{
  (e: 'preview-json', url: string): void
}>()

const handleLinkClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  const aTag = target.closest('a')
  
  // 拦截本地 json 下载链接
  if (aTag && aTag.href.includes('/downloads/') && aTag.href.endsWith('.json')) {
    e.preventDefault() // 阻止浏览器打开新标签页
    emit('preview-json', aTag.href) // 通知父组件打开弹窗
  }
}

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

// 渲染前预处理：防止大模型输出原始 Python 字典导致渲染失败
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
/* 解决链接不可见问题 */
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
  display: block;       /* 让表格变成块级元素，支持独立滚动 */
  max-width: 100%;      /* 最大宽度不超过外层聊天气泡 */
  width: max-content;   /* 宽度由内部数据撑开，实现自适应 */
  overflow-x: auto;     /* 只有当撑开的宽度大于 100% 时才出现横向滚动条 */
  
  table-layout: auto;
  border-collapse: separate;
  border-spacing: 0;
  margin: 1.25rem 0;
  border: 1px solid #374151;
  border-radius: 8px;
}

/* 单元格自适应撑开 */
.markdown-renderer th,
.markdown-renderer td {
  padding: 0.75rem 1.25rem; /* 增加左右内边距，防止自适应后数据拥挤 */
  border-bottom: 1px solid #374151;
  text-align: center;
  vertical-align: middle;
  white-space: nowrap; /* 强制所有列不换行，完整展示天文长数字 */
}

/* 修复底部最后一行的双重边框问题 */
.markdown-renderer tr:last-child td {
  border-bottom: none;
}

/* 斑马纹背景 */
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