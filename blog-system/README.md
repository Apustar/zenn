# Blog System - 个人博客系统

一个功能强大的前后端分离个人博客系统，参考 Halo Sakura 主题设计。

## 技术栈

### 后端
- Django 5.x
- Django REST Framework
- PostgreSQL / SQLite
- JWT 认证
- Session 管理（用于加密内容访问验证）

### 前端
- Vue 3 (Composition API)
- TypeScript
- Vite
- Pinia (状态管理)
- Vue Router
- Vue I18n (国际化)
- Axios
- Highlight.js (代码高亮)
- Lazysizes (图片懒加载)
- @iconify/vue (图标库)

## 项目结构

```
blog-system/
├── backend/          # Django 后端
│   ├── blog/         # 主应用配置
│   ├── posts/        # 文章模块
│   ├── categories/   # 分类模块
│   ├── tags/         # 标签模块
│   ├── comments/     # 评论模块
│   ├── users/        # 用户模块
│   ├── moments/      # 瞬间（说说）模块
│   ├── photos/       # 相册模块
│   ├── links/        # 友链模块
│   ├── settings/     # 站点设置模块
│   ├── music/        # 音乐模块
│   └── media/        # 媒体文件
├── frontend/         # Vue 前端
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── views/       # 页面视图
│   │   ├── router/      # 路由配置
│   │   ├── stores/      # Pinia 状态管理
│   │   ├── api/         # API 接口
│   │   ├── utils/       # 工具函数
│   │   └── locales/     # 国际化文件
│   └── public/
├── docs/             # 文档目录
│   └── ENCRYPTION_DESIGN.md  # 加密功能设计文档
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- Conda (用于 Python 环境管理)

### 后端设置

```bash
# 激活 conda 环境
conda activate blog

# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行迁移
python manage.py migrate

# 创建超级用户（用于访问 Django Admin）
python manage.py createsuperuser

# 运行开发服务器（默认 http://localhost:8000）
python manage.py runserver
```

### 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行开发服务器（默认 http://localhost:5173）
npm run dev

# 构建生产版本
npm run build
```

### 访问应用

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000/api/
- Django Admin：http://localhost:8000/admin/

## 功能特性

### 核心功能

#### 内容管理
- ✅ **文章管理**（CRUD）
  - Markdown 编辑器支持
  - 文章分类和标签
  - 文章置顶功能
  - 文章加密功能（密码保护）
  - 文章预览功能
  - 文章点赞和浏览统计
  - 文章搜索功能
  - 文章归档功能
  - 相关文章推荐

- ✅ **分类和标签系统**
  - 分类层级结构
  - 标签颜色自定义
  - 分类和标签统计

- ✅ **评论系统**
  - 支持回复评论（嵌套评论）
  - 评论点赞功能
  - 评论审核机制
  - 评论通知（待实现）

- ✅ **相册功能**
  - 相册管理
  - 照片上传和管理
  - 瀑布流布局
  - 相册加密功能（密码保护）

- ✅ **瞬间（说说）功能**
  - 发布瞬间
  - 瞬间点赞
  - 瞬间评论

- ✅ **友链管理**
  - 友链分类
  - 友链展示

#### 用户系统
- ✅ **JWT 用户认证**
  - 用户登录/登出
  - Token 自动刷新
  - 用户信息管理

#### 站点设置
- ✅ **站点配置**
  - 站点名称自定义
  - 站点图标上传（支持 PNG、JPG、SVG）
  - 站点描述和关键词
  - ICP 备案号设置

- ✅ **导航栏自定义**
  - 导航菜单项管理
  - 显示/隐藏控制
  - 排序功能
  - 访问权限控制

- ✅ **关于页面**
  - Markdown 内容支持
  - 后台编辑

#### 安全功能
- ✅ **内容加密**
  - 文章密码保护
  - 相册密码保护
  - Session 验证（30分钟有效期）
  - 密码修改后自动失效旧验证
  - 后端控制内容返回（前端无法绕过）

### 前端特性

- ✅ **主题系统**
  - 主题切换（Sakura、White、Dark）
  - 深色模式支持
  - 自定义主题背景

- ✅ **响应式设计**
  - 移动端适配
  - 平板适配
  - 桌面端优化

- ✅ **性能优化**
  - Pjax 无刷新导航
  - 图片懒加载
  - 代码高亮（Highlight.js）
  - SEO 优化（Meta 标签、Open Graph、Twitter Card）

- ✅ **国际化支持**
  - 中文/英文切换
  - 多语言内容管理

- ✅ **用户体验**
  - 回到顶部按钮
  - 加载状态提示
  - 错误处理
  - 平滑过渡动画

### 特色功能

#### 音乐播放器
- ✅ **音乐管理**
  - 音乐上传（支持 MP3、WAV、OGG）
  - 封面图上传
  - 歌词支持
  - 音乐排序

- ✅ **播放器功能**
  - 播放/暂停控制
  - 上一曲/下一曲
  - 播放模式切换（顺序/循环/随机）
  - 音量控制
  - 播放列表管理
  - 进度条控制
  - 折叠/展开设计（右上角圆形图标）

#### 文章分享
- ✅ **分享功能**
  - 一键复制文章链接
  - 分享到微博
  - 分享到 Twitter
  - 分享到 QQ
  - 复制成功提示

### 页面功能

- ✅ **首页**
  - 首屏展示
  - 文章列表
  - 分页功能

- ✅ **文章详情页**
  - Markdown 渲染
  - 代码高亮
  - 文章分享
  - 评论展示
  - 相关文章推荐

- ✅ **分类和标签页面**
  - 文章列表展示
  - 分页功能

- ✅ **文章归档页面**
  - 按时间归档
  - 文章列表展示

- ✅ **瞬间页面**
  - 瞬间列表
  - 发布瞬间（需登录）

- ✅ **相册页面**
  - 相册列表
  - 瀑布流布局

- ✅ **友链页面**
  - 友链分类展示
  - 友链列表

- ✅ **关于页面**
  - Markdown 内容展示

- ✅ **搜索页面**
  - 全文搜索
  - 搜索结果展示

## API 端点

### 文章
- `GET /api/posts/` - 获取文章列表
- `GET /api/posts/{slug}/` - 获取文章详情
- `POST /api/posts/` - 创建文章（需认证）
- `PATCH /api/posts/{slug}/` - 更新文章（需认证）
- `DELETE /api/posts/{slug}/` - 删除文章（需认证）
- `POST /api/posts/{slug}/like/` - 点赞文章
- `GET /api/posts/{slug}/related/` - 获取相关文章
- `GET /api/posts/archives/` - 获取归档
- `POST /api/posts/{slug}/verify_password/` - 验证文章密码

### 分类
- `GET /api/categories/` - 获取分类列表
- `GET /api/categories/{slug}/` - 获取分类详情

### 标签
- `GET /api/tags/` - 获取标签列表
- `GET /api/tags/{slug}/` - 获取标签详情

### 评论
- `GET /api/comments/` - 获取评论列表
- `POST /api/comments/` - 创建评论（需认证）
- `POST /api/comments/{id}/like/` - 点赞评论（需认证）

### 用户
- `GET /api/users/` - 获取用户列表
- `GET /api/users/{id}/` - 获取用户详情
- `GET /api/users/me/` - 获取当前用户（需认证）

### 认证
- `POST /api/auth/login/` - 登录
- `POST /api/auth/refresh/` - 刷新 Token

### 瞬间
- `GET /api/moments/` - 获取瞬间列表
- `POST /api/moments/` - 创建瞬间（需认证）
- `POST /api/moments/{id}/like/` - 点赞瞬间

### 相册
- `GET /api/photos/albums/` - 获取相册列表
- `GET /api/photos/albums/{slug}/` - 获取相册详情
- `POST /api/photos/albums/{slug}/verify_password/` - 验证相册密码

### 友链
- `GET /api/links/categories/` - 获取友链分类列表

### 站点设置
- `GET /api/settings/` - 获取站点设置
- `PATCH /api/settings/{id}/` - 更新站点设置（需管理员权限）
- `GET /api/navigation/` - 获取导航菜单
- `POST /api/navigation/` - 创建导航项（需管理员权限）
- `PATCH /api/navigation/{id}/` - 更新导航项（需管理员权限）
- `DELETE /api/navigation/{id}/` - 删除导航项（需管理员权限）

### 音乐
- `GET /api/music/` - 获取音乐列表
- `GET /api/music/{id}/` - 获取音乐详情
- `POST /api/music/` - 创建音乐（需认证）
- `PATCH /api/music/{id}/` - 更新音乐（需认证）
- `DELETE /api/music/{id}/` - 删除音乐（需认证）

## 文档

- [部署指南](./DEPLOYMENT.md)
- [更新日志](./CHANGELOG.md)
- [加密功能设计文档](./docs/ENCRYPTION_DESIGN.md)

## 开发说明

### 代码规范

- 前端使用 TypeScript 严格模式
- 遵循 Vue 3 Composition API 最佳实践
- 后端遵循 Django 最佳实践
- 所有 API 使用 RESTful 风格

### 调试模式

开发环境下，错误信息会在控制台输出。生产环境下，错误会被静默处理，避免泄露敏感信息。

### 环境变量

后端环境变量在 `backend/blog/settings.py` 中配置。
前端环境变量通过 Vite 的 `import.meta.env` 访问。

## 待开发功能

- [ ] 文章目录（TOC）自动生成
- [ ] 阅读统计和热门文章
- [ ] 邮件通知功能
- [ ] RSS 订阅
- [ ] 更多主题样式
- [ ] 文章草稿自动保存
- [ ] 文章版本历史
- [ ] 全文搜索优化（Elasticsearch）

## 许可证

MIT License
