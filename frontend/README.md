# AI Agent 前端应用

基于 Vue 3 + TypeScript + Vite 构建的现代化智能助手前端应用。

## 技术栈

- **核心框架**: Vue 3.5+ (Composition API)
- **构建工具**: Vite 6+
- **开发语言**: TypeScript 5.9+
- **UI组件库**: Naive UI 2.44+
- **样式方案**: TailwindCSS 4.2+
- **状态管理**: Pinia 3+
- **路由管理**: Vue Router 5+
- **HTTP客户端**: Axios + Fetch API
- **实时通信**: Server-Sent Events (SSE) + @vueuse/core
- **工具函数**: lodash-es, dayjs
- **图标库**: @vicons/ionicons5, @vicons/fa

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 公共组件
│   ├── composables/     # 组合式函数
│   │   └── useSSE.ts    # SSE通信模块
│   ├── layouts/         # 布局组件
│   │   └── AppLayout.vue
│   ├── router/          # 路由配置
│   │   └── index.ts
│   ├── stores/          # Pinia状态管理
│   │   └── app.ts
│   ├── styles/          # 样式文件
│   │   └── tailwind.css
│   ├── types/           # TypeScript类型定义
│   │   └── index.ts
│   ├── views/           # 页面视图
│   │   ├── HomeView.vue
│   │   ├── ChatView.vue
│   │   ├── AboutView.vue
│   │   └── NotFoundView.vue
│   ├── App.vue          # 根组件
│   └── main.ts          # 入口文件
├── public/              # 公共资源
├── dist/                # 构建输出
├── netlify.toml         # Netlify部署配置
├── .env.development     # 开发环境变量
├── .env.production      # 生产环境变量
├── vite.config.ts       # Vite配置
├── tsconfig.json        # TypeScript配置
└── package.json         # 依赖管理
```

## 核心功能

### 1. 实时通信 (SSE)
- 使用 `@vueuse/core` 的 `useEventSource` 实现
- 支持自动重连机制
- 心跳检测保持连接稳定
- 类型安全的消息解析

### 2. 响应式设计
- 基于 TailwindCSS 的原子化CSS
- 移动端优先的响应式布局
- Naive UI 组件库适配

### 3. 状态管理
- Pinia 集中管理应用状态
- 连接状态、消息历史、错误处理

### 4. 路由管理
- Vue Router 5 实现SPA导航
- 路由守卫设置页面标题
- KeepAlive 缓存页面状态

## 开发指南

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```
访问 http://localhost:3000

### 构建生产版本
```bash
npm run build
```

### 代码检查
```bash
npm run lint
npm run format
```

### 类型检查
```bash
npm run type-check
```

## 环境变量

### 开发环境 (.env.development)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_SSE_ENDPOINT=/api/sse
VITE_DEBUG=true
```

### 生产环境 (.env.production)
```
VITE_API_BASE_URL=https://your-api-domain.com
VITE_SSE_ENDPOINT=/api/sse
VITE_DEBUG=false
```

## 部署

### Netlify 部署

1. **通过Git部署**
   - 将代码推送到GitHub/GitLab
   - 在Netlify中连接仓库
   - 配置构建设置：
     - Build command: `npm run build`
     - Publish directory: `dist`

2. **使用Netlify CLI**
   ```bash
   # 安装CLI
   npm install -g netlify-cli

   # 登录
   netlify login

   # 初始化站点
   netlify init

   # 部署
   netlify deploy --prod --dir=dist
   ```

3. **配置说明**
   - `netlify.toml` 已包含完整配置
   - 支持SPA路由重写
   - API代理配置
   - 安全头设置
   - 静态资源缓存

## 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 性能优化

- Vite 按需编译，快速冷启动
- 代码分割和懒加载
- 组件级KeepAlive缓存
- 静态资源长期缓存
- Tree-shaking优化

## 许可证

MIT License
