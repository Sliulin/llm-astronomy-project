<template>
  <div 
    class="markdown-renderer text-gray-200 leading-relaxed max-w-none" 
    v-html="renderedContent"
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

// 初始化 Markdown 解析器
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  typographer: true
}).use(markdownItKatex)

// 渲染前预处理：防止大模型吐出原始 Python 字典导致的渲染失败
const preprocessContent = (text: string) => {
  if (!text) return ''
  
  // 如果内容看起来像原始 JSON/字典（比如包含 {'links': ...}），给它包裹代码块，防止乱码
  if (text.trim().startsWith('{') && text.includes("'links'")) {
    return '```json\n' + text + '\n```'
  }
  
  // 修复常见的 Markdown 链接空格错误：将 "[描述] (http)" 替换为 "[描述](http)"
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
  color: #60a5fa !important; /* 强制亮蓝色 */
  text-decoration: underline !important; /* 强制下划线 */
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
.markdown-renderer a[href$=".fits"]::before {
  content: "📥 ";
  text-decoration: none;
  display: inline-block;
}

/* 表格样式美化 - 适配天文星表数据 */
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

/* 将所有表头和单元格内容居中 */
.markdown-renderer th,
.markdown-renderer td {
  padding: 0.75rem;
  border-bottom: 1px solid #374151;
  text-align: center; /* 核心修改：全局居中 */
  vertical-align: middle;
}

/* 核心修改：智能控制第一列（通常是编号或名称）的宽度 */
.markdown-renderer th:first-child,
.markdown-renderer td:first-child {
  /* 基础宽度设为 80px (约 4-5 个中文字符的宽度) */
  width: 100px; 
  /* 保证内容过长时不会被强制截断，而是自然撑开或换行 */
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

/* 修复底部最后一行的双重边框问题 */
.markdown-renderer tr:last-child td {
  border-bottom: none;
}

/* 斑马纹背景 */
.markdown-renderer tr:nth-child(even) td {
  background-color: rgba(55, 65, 81, 0.3);
}

/* 物理公式样式微调 */
.katex-display {
  margin: 1rem 0;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  overflow-x: auto;
}

/* 段落间距 */
.markdown-renderer p {
  margin-bottom: 1rem;
}
</style>