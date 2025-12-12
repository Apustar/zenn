"""
相册加密相关的工具函数（复用posts的工具函数）
"""
from posts.utils import (
    verify_content_password,
    hash_content_password,
    get_password_version_for_session,
    check_password_verified_in_session,
    mark_password_verified_in_session
)

__all__ = [
    'verify_content_password',
    'hash_content_password',
    'get_password_version_for_session',
    'check_password_verified_in_session',
    'mark_password_verified_in_session',
]

