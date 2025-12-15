"""
文章加密相关的工具函数
"""
import hashlib
import re
from django.contrib.auth.hashers import check_password, make_password
from django.utils.text import slugify


def verify_content_password(content_password_hash, input_password):
    """验证内容密码"""
    if not content_password_hash:
        return False
    # 使用Django的密码验证
    return check_password(input_password, content_password_hash)


def hash_content_password(password):
    """对内容密码进行哈希"""
    if not password:
        return ''
    return make_password(password)


def get_password_version_for_session(content_type, content_id, password_updated_at):
    """生成用于session的密码版本标识（用于检测密码是否被修改）"""
    # 使用内容ID和密码更新时间生成一个标识
    if password_updated_at:
        # 将datetime转换为timestamp字符串
        timestamp = password_updated_at.timestamp()
        combined = f"{content_type}_{content_id}_{timestamp}"
    else:
        # 如果没有更新时间，使用内容ID
        combined = f"{content_type}_{content_id}_none"
    return hashlib.md5(combined.encode()).hexdigest()


def check_password_verified_in_session(request, content_type, content_id, password_updated_at):
    """检查session中是否已验证过密码（且密码未被修改）"""
    session_key = f'verified_{content_type}_{content_id}'
    verified_version = request.session.get(session_key)
    
    if not verified_version:
        return False
    
    # 检查密码是否被修改过（通过比较密码更新时间）
    current_version = get_password_version_for_session(content_type, content_id, password_updated_at)
    return verified_version == current_version


def mark_password_verified_in_session(request, content_type, content_id, password_updated_at):
    """在session中标记密码已验证"""
    session_key = f'verified_{content_type}_{content_id}'
    verified_version = get_password_version_for_session(content_type, content_id, password_updated_at)
    request.session[session_key] = verified_version
    request.session.modified = True  # 确保session被保存


def extract_toc_from_markdown(content):
    """
    从 Markdown 内容中提取目录结构
    
    Args:
        content: Markdown 文本内容
        
    Returns:
        list: TOC 列表，每个元素包含 level, text, id, children
    """
    if not content:
        return []
    
    toc = []
    lines = content.split('\n')
    
    for line in lines:
        # 匹配 Markdown 标题 (# ## ### 等)
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))  # 标题级别 (1-6)
            text = match.group(2).strip()  # 标题文本
            
            # 生成 ID（基于标题文本）
            heading_id = slugify(text)
            
            # 如果 ID 为空（标题全是特殊字符），使用序号
            if not heading_id:
                heading_id = f'heading-{len(toc) + 1}'
            
            # 确保 ID 唯一性
            base_id = heading_id
            counter = 1
            while any(item['id'] == heading_id for item in toc):
                heading_id = f'{base_id}-{counter}'
                counter += 1
            
            toc.append({
                'level': level,
                'text': text,
                'id': heading_id,
                'children': []
            })
    
    # 构建层级结构
    return _build_toc_hierarchy(toc)


def _build_toc_hierarchy(toc_items):
    """
    将扁平的 TOC 列表构建成层级结构
    
    Args:
        toc_items: 扁平化的 TOC 列表
        
    Returns:
        list: 层级化的 TOC 列表
    """
    if not toc_items:
        return []
    
    result = []
    stack = []  # 用于跟踪当前路径
    
    for item in toc_items:
        level = item['level']
        
        # 移除栈中级别大于等于当前级别的项
        while stack and stack[-1]['level'] >= level:
            stack.pop()
        
        # 构建新的项（不包含 children，稍后添加）
        new_item = {
            'level': level,
            'text': item['text'],
            'id': item['id'],
            'children': []
        }
        
        if stack:
            # 添加到父级的 children
            stack[-1]['children'].append(new_item)
        else:
            # 顶级项
            result.append(new_item)
        
        # 将当前项加入栈
        stack.append(new_item)
    
    return result


def add_ids_to_html_headings(html_content):
    """
    为 HTML 中的标题添加 ID 属性
    
    Args:
        html_content: HTML 内容字符串
        
    Returns:
        str: 添加了 ID 的 HTML 内容
    """
    if not html_content:
        return html_content
    
    # 匹配 h1-h6 标签（包括自闭合标签的情况，但标题不会是自闭合的）
    def add_id(match):
        full_match = match.group(0)
        tag = match.group(1).lower()  # h1, h2, etc. (转为小写)
        attrs = match.group(2) or ''  # 现有属性
        text = match.group(3)  # 标题文本
        
        # 如果已经有 id 属性，不处理
        if re.search(r'\bid\s*=', attrs, re.IGNORECASE):
            return full_match
        
        # 清理文本（移除 HTML 标签）
        text_clean = re.sub(r'<[^>]+>', '', text).strip()
        if not text_clean:
            return full_match
        
        # 生成 ID
        heading_id = slugify(text_clean)
        if not heading_id:
            # 如果标题全是特殊字符，生成一个简单的 ID
            import hashlib
            heading_id = f'h{hashlib.md5(text_clean.encode()).hexdigest()[:8]}'
        
        # 确保 ID 唯一性（简单处理，实际应该在整个文档范围内检查）
        # 这里只做基本处理，完整处理需要在调用前进行
        
        # 添加 id 属性
        if attrs.strip():
            # 如果已有属性，在末尾添加
            new_attrs = f'{attrs} id="{heading_id}"'
        else:
            # 如果没有属性，直接添加
            new_attrs = f'id="{heading_id}"'
        
        return f'<{tag} {new_attrs}>{text}</{tag}>'
    
    # 匹配 <h1>到<h6>标签，支持有/无属性
    # 使用非贪婪匹配，并处理嵌套标签的情况
    pattern = r'<([hH][1-6])([^>]*)>(.*?)</\1>'
    html_content = re.sub(pattern, add_id, html_content, flags=re.DOTALL)
    
    return html_content

