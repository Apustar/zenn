# Blog System - 个人博客系统

一个功能强大的前后端分离个人博客系统，参考 Halo Sakura 主题设计。

## 技术栈

### 后端
- Django 5.x
- Django REST Framework
- PostgreSQL / SQLite
- JWT 认证

### 前端
- Vue 3
- TypeScript
- Vite
- Pinia (状态管理)
- Vue Router
- Axios

## 项目结构

```
blog-system/
├── backend/          # Django 后端
│   ├── blog/         # 主应用
│   ├── posts/        # 文章模块
│   ├── categories/   # 分类模块
│   ├── tags/         # 标签模块
│   ├── comments/     # 评论模块
│   ├── users/        # 用户模块
│   └── media/        # 媒体文件
├── frontend/         # Vue 前端
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   ├── stores/
│   │   └── utils/
│   └── public/
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

### 已实现功能

#### 核心功能
- ✅ 文章管理（CRUD）
- ✅ 分类和标签系统
- ✅ 评论系统（支持回复和点赞）
- ✅ JWT 用户认证
- ✅ 媒体文件管理
- ✅ 文章搜索功能

#### 前端特性
- ✅ 主题切换（参考 Sakura 主题）
- ✅ 深色模式
- ✅ 响应式设计
- ✅ Pjax 无刷新导航
- ✅ 图片懒加载
- ✅ 代码高亮（Highlight.js）
- ✅ SEO 优化（Meta 标签、Open Graph、Twitter Card）
- ✅ 国际化支持（中文/英文）

#### 页面功能
- ✅ 首页（首屏 + 文章列表）
- ✅ 文章详情页（Markdown 渲染）
- ✅ 分类和标签页面
- ✅ 文章归档页面
- ✅ 瞬间（说说）功能
- ✅ 相册功能（瀑布流布局）
- ✅ 友链管理页面

### 待开发功能

- [ ] 音乐播放器集成
- [ ] 文章目录（TOC）自动生成
- [ ] 文章分享功能
- [ ] 阅读统计和热门文章
- [ ] 邮件通知功能
- [ ] RSS 订阅
- [ ] 更多主题样式

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

## 许可证

MIT License

