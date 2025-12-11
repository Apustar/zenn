# 更新日志

## [1.0.0] - 2024-12-11

### 新增功能

#### 核心功能
- ✨ 文章管理系统（CRUD）
- ✨ 分类和标签系统
- ✨ 评论系统（支持回复和点赞）
- ✨ JWT 用户认证
- ✨ 媒体文件管理

#### 前端特性
- ✨ 主题切换功能（参考 Sakura 主题设计）
- ✨ 深色模式支持
- ✨ 响应式设计（移动端适配）
- ✨ Pjax 无刷新导航
- ✨ 图片懒加载
- ✨ 代码高亮（Highlight.js）
- ✨ SEO 优化（Meta 标签、Open Graph、Twitter Card）
- ✨ 国际化支持（中文/英文）

#### 页面功能
- ✨ 首页（首屏 + 文章列表）
- ✨ 文章详情页（Markdown 渲染）
- ✨ 分类和标签页面
- ✨ 文章归档页面
- ✨ 瞬间（说说）功能
- ✨ 相册功能（瀑布流布局）
- ✨ 友链管理页面

### 技术栈

#### 后端
- Django 4.x
- Django REST Framework
- JWT 认证
- SQLite/PostgreSQL

#### 前端
- Vue 3 (Composition API)
- TypeScript
- Vite
- Pinia (状态管理)
- Vue Router
- Vue I18n
- Axios
- Highlight.js
- Lazysizes

### 已知问题

- Pjax 功能暂时禁用（避免影响页面显示）
- ContentType ID 需要手动配置（评论功能）
- 部分组件国际化翻译待完善

### 下一步计划

- [ ] 音乐播放器集成
- [ ] 文章目录（TOC）自动生成
- [ ] 文章分享功能
- [ ] 阅读统计和热门文章
- [ ] 邮件通知功能
- [ ] RSS 订阅
- [ ] 更多主题样式

