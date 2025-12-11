# 部署指南

## 后端部署

### 使用 Gunicorn + Nginx

1. 安装 Gunicorn
```bash
pip install gunicorn
```

2. 收集静态文件
```bash
python manage.py collectstatic --noinput
```

3. 运行 Gunicorn
```bash
gunicorn blog.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

4. 配置 Nginx（示例）
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/blog-system/backend/staticfiles/;
    }

    location /media/ {
        alias /path/to/blog-system/backend/media/;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 前端部署

### 构建生产版本

```bash
cd frontend
npm run build
```

构建后的文件在 `frontend/dist/` 目录中。

### 使用 Nginx 部署

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/blog-system/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 环境变量配置

### 后端 (.env)

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@localhost:5432/blogdb
```

### 前端

在 `vite.config.ts` 中配置生产环境的 API 地址。

## 数据库迁移

```bash
python manage.py migrate
```

## 创建超级用户

```bash
python manage.py createsuperuser
```

## 注意事项

1. 生产环境务必设置 `DEBUG=False`
2. 使用强密码的 `SECRET_KEY`
3. 配置 HTTPS
4. 定期备份数据库
5. 设置适当的文件权限

