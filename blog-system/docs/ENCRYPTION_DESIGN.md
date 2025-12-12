# 内容加密功能设计文档

## 目录

1. [概述](#概述)
2. [设计原则](#设计原则)
3. [架构设计](#架构设计)
4. [安全机制](#安全机制)
5. [实现细节](#实现细节)
6. [安全优势](#安全优势)
7. [使用指南](#使用指南)

---

## 概述

本文档详细说明了博客系统中文章和相册加密功能的设计思路、实现原理和安全机制。该设计采用**后端控制内容返回**的核心思想，确保即使前端被修改，也无法获取未授权的内容。

### 功能特性

- ✅ 文章和相册支持密码加密
- ✅ 加密内容未验证时只显示预览
- ✅ 密码验证后30分钟内无需重复输入
- ✅ 密码修改后自动失效旧验证
- ✅ 前端无法绕过加密获取完整内容
- ✅ 支持未登录访客的session验证

---

## 设计原则

### 1. 最小权限原则（Principle of Least Privilege）

**只返回用户有权查看的内容**

- 未验证用户：只返回预览内容（前500字符）
- 已验证用户：返回完整内容
- 管理员：直接访问所有内容

### 2. 后端验证原则（Backend Validation）

**所有安全逻辑在后端实现**

- 前端只负责展示，不包含任何安全判断
- 验证状态由后端session管理
- API响应根据验证状态动态生成

### 3. 防御深度（Defense in Depth）

**多层防护机制**

```
数据库层 → API层 → Session层 → 前端层
```

每一层都有独立的保护机制，即使一层失效，其他层仍能提供保护。

### 4. 状态管理（State Management）

**使用session跟踪验证状态**

- 基于密码更新时间生成版本标识
- 密码修改后自动失效旧验证
- Session过期时间30分钟

---

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────┐
│  1. 数据库层：密码哈希存储          │
│     - 密码使用Django哈希算法        │
│     - password_updated_at跟踪修改   │
│     - 即使数据库泄露也无法还原      │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  2. API层：内容过滤                 │
│     - 序列化器控制返回内容          │
│     - 未验证不返回完整数据          │
│     - 只返回preview_content_html    │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  3. Session层：验证状态管理         │
│     - 基于时间戳的版本控制          │
│     - 密码修改自动失效              │
│     - 30分钟过期时间                │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  4. 前端层：仅渲染                  │
│     - 只显示后端返回的数据          │
│     - 无法获取未返回的内容          │
│     - 密码输入弹窗                  │
└─────────────────────────────────────┘
```

### 数据流

```
用户请求文章
    ↓
后端检查is_encrypted
    ↓
是 → 检查session验证状态
    ↓
未验证 → 返回预览内容（preview_content_html）
    ↓
已验证 → 返回完整内容（content_html）
    ↓
前端渲染对应内容
```

---

## 安全机制

### 1. 密码存储安全

#### 模型字段

```python
class Post(models.Model):
    is_encrypted = models.BooleanField(default=False)
    password = models.CharField(max_length=128, blank=True)
    password_updated_at = models.DateTimeField(null=True, blank=True)
```

#### 密码哈希

- 使用Django的`make_password()`函数
- 采用PBKDF2算法
- 每次哈希结果不同（包含随机salt）
- 即使相同密码，哈希值也不同

```python
def save(self, *args, **kwargs):
    if self.is_encrypted and self.password:
        if not self.password.startswith('pbkdf2_sha256$'):
            # 明文密码，需要哈希
            self.password = hash_content_password(self.password)
            password_changed = True
    
    if password_changed:
        self.password_updated_at = timezone.now()
```

### 2. 内容过滤机制

#### 序列化器实现

**关键代码：`PostDetailSerializer.to_representation()`**

```python
def to_representation(self, instance):
    """重写序列化方法，根据验证状态决定返回的内容"""
    data = super().to_representation(instance)
    
    # 如果是加密文章且未验证，隐藏完整内容
    if instance.is_encrypted and not data.get('is_password_verified'):
        data['content'] = None          # 不返回完整内容
        data['content_html'] = None     # 不返回完整HTML
        # 只返回 preview_content_html（前500字符）
    
    return data
```

**验证状态检查：`get_is_password_verified()`**

```python
def get_is_password_verified(self, obj):
    """检查密码是否已验证"""
    request = self.context.get('request')
    
    # 未加密视为已验证
    if not obj.is_encrypted:
        return True
    
    # 管理员直接访问
    if request.user.is_authenticated and request.user.is_staff:
        return True
    
    # 检查session验证状态
    return check_password_verified_in_session(
        request, 'post', obj.id, obj.password_updated_at
    )
```

### 3. Session验证机制

#### 版本标识生成

```python
def get_password_version_for_session(content_type, content_id, password_updated_at):
    """生成用于session的密码版本标识"""
    if password_updated_at:
        timestamp = password_updated_at.timestamp()
        combined = f"{content_type}_{content_id}_{timestamp}"
    else:
        combined = f"{content_type}_{content_id}_none"
    
    return hashlib.md5(combined.encode()).hexdigest()
```

**工作原理：**

1. 使用`content_type`、`content_id`和`password_updated_at`时间戳生成唯一标识
2. 密码修改后，`password_updated_at`更新，标识改变
3. Session中存储的旧标识失效，需要重新验证

#### 验证状态检查

```python
def check_password_verified_in_session(request, content_type, content_id, password_updated_at):
    """检查session中是否已验证过密码（且密码未被修改）"""
    session_key = f'verified_{content_type}_{content_id}'
    verified_version = request.session.get(session_key)
    
    if not verified_version:
        return False
    
    # 检查密码是否被修改过
    current_version = get_password_version_for_session(
        content_type, content_id, password_updated_at
    )
    return verified_version == current_version
```

#### 标记验证成功

```python
def mark_password_verified_in_session(request, content_type, content_id, password_updated_at):
    """在session中标记密码已验证"""
    session_key = f'verified_{content_type}_{content_id}'
    verified_version = get_password_version_for_session(
        content_type, content_id, password_updated_at
    )
    request.session[session_key] = verified_version
    request.session.modified = True
```

### 4. 密码修改检测

#### 密码变更检测逻辑

```python
def save(self, *args, **kwargs):
    password_changed = False
    
    # 获取旧的密码
    old_password = None
    if self.pk:
        try:
            old_instance = Post.objects.get(pk=self.pk)
            old_password = old_instance.password
        except Post.DoesNotExist:
            pass
    
    if self.is_encrypted and self.password:
        if not self.password.startswith('pbkdf2_sha256$'):
            # 明文密码，需要哈希
            new_password_hash = hash_content_password(self.password)
            # 检查密码是否真的改变了
            if old_password != new_password_hash:
                password_changed = True
            self.password = new_password_hash
        else:
            # 已经是哈希格式，直接比较
            if old_password != self.password:
                password_changed = True
    
    # 如果密码被修改，更新 password_updated_at
    if password_changed:
        self.password_updated_at = timezone.now()
```

**检测场景：**

1. **首次设置密码**：`old_password`为`None`，`new_password_hash`为新值 → `password_changed = True`
2. **修改密码**：`old_password` ≠ `new_password_hash` → `password_changed = True`
3. **取消加密**：`old_password`存在，`self.password`为空 → `password_changed = True`
4. **未修改密码**：`old_password` == `self.password` → `password_changed = False`

---

## 实现细节

### 后端实现

#### 1. 模型层（Models）

**文件：`backend/posts/models.py` 和 `backend/photos/models.py`**

- `is_encrypted`: 是否加密标志
- `password`: 密码哈希值
- `password_updated_at`: 密码更新时间（用于检测修改）

#### 2. 工具函数层（Utils）

**文件：`backend/posts/utils.py`**

- `verify_content_password()`: 验证密码
- `hash_content_password()`: 密码哈希
- `get_password_version_for_session()`: 生成版本标识
- `check_password_verified_in_session()`: 检查验证状态
- `mark_password_verified_in_session()`: 标记验证成功

#### 3. 序列化器层（Serializers）

**文件：`backend/posts/serializers.py` 和 `backend/photos/serializers.py`**

- `get_is_password_verified()`: 检查验证状态
- `get_preview_content_html()`: 生成预览内容
- `to_representation()`: 控制返回内容

#### 4. 视图层（Views）

**文件：`backend/posts/views.py` 和 `backend/photos/views.py`**

- `verify_password` action: 密码验证API端点
- 确保序列化器接收`request` context

### 前端实现

#### 1. API层

**文件：`frontend/src/api/posts.ts` 和 `frontend/src/api/photos.ts`**

```typescript
// 验证文章密码
verifyPassword: async (slug: string, password: string) => {
  return api.post(`/posts/${slug}/verify_password/`, { password })
}
```

#### 2. 组件层

**密码输入弹窗：`frontend/src/components/PasswordModal.vue`**

- 密码输入框
- 错误提示
- 加载状态
- 自动聚焦

**文章页面：`frontend/src/views/Post.vue`**

```vue
<!-- 加密文章预览 -->
<div v-if="post.is_encrypted && !post.is_password_verified">
  <div v-html="post.preview_content_html"></div>
  <button @click="showPasswordModal = true">查看全文</button>
</div>

<!-- 完整内容 -->
<div v-else v-html="post.content_html"></div>
```

**相册页面：`frontend/src/views/Album.vue`**

- 加密相册显示锁定提示
- 密码验证后显示照片

#### 3. API配置

**文件：`frontend/src/api/index.ts`**

```typescript
const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // 允许发送cookies（用于session）
})
```

---

## 安全优势

### 与不安全设计的对比

#### ❌ 不安全设计（前端控制）

```javascript
// 不安全：完整内容已加载到页面
const fullContent = encryptedContent;
if (!isVerified) {
  document.getElementById('content').style.display = 'none';
  document.getElementById('preview').style.display = 'block';
}
```

**问题：**

1. 完整内容已加载到DOM中
2. 通过开发者工具可以查看
3. 通过JavaScript可以访问
4. 网络请求中包含完整内容

#### ✅ 安全设计（后端控制）

**优势：**

1. **内容不在前端**：未验证时，完整内容不会发送到前端
2. **无法绕过**：即使修改前端代码，也无法获取后端未返回的数据
3. **网络请求安全**：API响应中不包含完整内容
4. **密码修改检测**：密码修改后，旧session失效

### 安全测试场景

#### 场景1：修改前端HTML

**操作：** 使用开发者工具删除加密提示，显示完整内容

**结果：** ❌ 失败 - 完整内容不在DOM中，无法显示

**原因：** 后端未返回`content_html`，前端没有数据可渲染

#### 场景2：修改JavaScript

**操作：** 修改前端代码，强制显示完整内容

**结果：** ❌ 失败 - 无法获取未返回的数据

**原因：** API响应中`content_html`为`null`，JavaScript无法凭空创建内容

#### 场景3：拦截网络请求

**操作：** 使用抓包工具拦截API响应

**结果：** ❌ 失败 - 响应中只包含预览内容

**原因：** 序列化器在返回前已过滤完整内容

#### 场景4：修改Session

**操作：** 尝试修改session中的验证标识

**结果：** ⚠️ 可能成功，但密码修改后会失效

**原因：** 密码修改后，`password_updated_at`更新，旧标识失效

---

## 使用指南

### 后端配置

#### 1. 数据库迁移

```bash
cd blog-system/backend
python manage.py makemigrations posts photos
python manage.py migrate
```

#### 2. Session配置

**文件：`backend/blog/settings.py`**

```python
# Session 配置（用于加密内容访问验证）
SESSION_COOKIE_AGE = 1800  # 30分钟（秒）
SESSION_SAVE_EVERY_REQUEST = True  # 每次请求都保存session
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # 关闭浏览器不立即过期
```

### 使用步骤

#### 1. 在后台设置加密

1. 进入Django Admin
2. 编辑文章或相册
3. 勾选"是否加密"
4. 输入访问密码
5. 保存

#### 2. 用户访问流程

1. **访问加密内容**
   - 文章：显示预览内容（前500字符）
   - 相册：显示锁定提示

2. **输入密码**
   - 点击"查看全文"或"输入密码"
   - 弹出密码输入框
   - 输入正确密码

3. **验证成功**
   - 显示完整内容
   - Session中记录验证状态
   - 30分钟内无需重复输入

4. **密码修改后**
   - 旧session失效
   - 需要重新输入新密码

### API端点

#### 验证文章密码

```
POST /api/posts/{slug}/verify_password/
Content-Type: application/json

{
  "password": "your_password"
}
```

**响应：**

```json
{
  "success": true,
  "message": "密码验证成功"
}
```

#### 验证相册密码

```
POST /api/albums/{slug}/verify_password/
Content-Type: application/json

{
  "password": "your_password"
}
```

---

## 总结

### 核心设计思想

**后端控制内容返回** - 这是整个安全设计的核心。前端只负责展示，后端决定返回什么数据。

### 关键安全机制

1. **密码哈希存储**：使用Django的PBKDF2算法
2. **内容过滤**：序列化器控制返回内容
3. **Session验证**：基于时间戳的版本控制
4. **密码修改检测**：自动失效旧验证

### 设计优势

- ✅ 前端无法绕过加密
- ✅ 网络请求中不包含完整内容
- ✅ 密码修改后自动失效
- ✅ 符合Web安全最佳实践

### 适用场景

- 个人博客的私密文章
- 付费内容的预览
- 会员专属内容
- 需要密码保护的相册

---

## 参考资料

- [Django Session文档](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
- [Django密码哈希](https://docs.djangoproject.com/en/stable/topics/auth/passwords/)
- [OWASP安全指南](https://owasp.org/www-project-web-security-testing-guide/)
- [REST API安全最佳实践](https://restfulapi.net/security-essentials/)

---

**文档版本：** 1.0  
**最后更新：** 2024年12月  
**作者：** AI Assistant

