"""
通用响应格式和异常处理
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError


def api_response(data=None, message="Success", code=status.HTTP_200_OK, success=True):
    """
    统一API响应格式
    """
    response_data = {
        'success': success,
        'message': message,
        'code': code,
        'data': data
    }
    return Response(response_data, status=code)


def api_error_response(message="Error", code=status.HTTP_400_BAD_REQUEST, errors=None):
    """
    统一错误响应格式
    """
    response_data = {
        'success': False,
        'message': message,
        'code': code,
        'errors': errors
    }
    return Response(response_data, status=code)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    """
    # 调用DRF默认的异常处理器
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': '',
            'code': response.status_code,
            'errors': response.data
        }
        
        # 根据异常类型设置消息
        if isinstance(exc, Http404):
            custom_response_data['message'] = '资源不存在'
        elif isinstance(exc, PermissionDenied):
            custom_response_data['message'] = '权限不足'
        elif isinstance(exc, ValidationError):
            custom_response_data['message'] = '数据验证失败'
        else:
            custom_response_data['message'] = str(exc)
        
        response.data = custom_response_data
    
    return response


class APIException(Exception):
    """
    自定义API异常
    """
    def __init__(self, message="API Error", code=status.HTTP_400_BAD_REQUEST, errors=None):
        self.message = message
        self.code = code
        self.errors = errors
        super().__init__(message)