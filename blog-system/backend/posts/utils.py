"""
文章加密相关的工具函数
"""
import hashlib
from django.contrib.auth.hashers import check_password, make_password


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

