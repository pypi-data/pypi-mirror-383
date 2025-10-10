# -*- coding: utf-8 -*-
class BizException(Exception):
    def __init__(self, message: str, code: int = -1):
        self.message = message
        self.code = code


class NoAuthException(Exception):
    def __init__(self, message: str = '权限不足'):
        self.message = message
        self.code = 401


# 系统错误类异常
class SystemException(Exception):
    def __init__(self, message: str = '系统异常，请联系管理员处理'):
        self.message = message
        self.code = 500


# 系统参数为配置
class NoConfigException(SystemException):
    def __init__(self, message: str = '系统参数配置异常'):
        self.message = message
        self.code = 500


class MQConnectionException(SystemException):
    """RabbitMQ连接异常"""

    def __init__(self, message="MQ connection failed"):
        super().__init__(message)


# -----------
# 采集专用
# -----------

# 需要重试的请求统一包装
class RetryRequest(Exception):
    def __init__(self, ex=None):
        self.ex = ex


# 后端专用异常类型，信息不直接暴露给前端
class BackendException(Exception):
    def __init__(self, message: str = '服务端异常'):
        self.message = message


# 代理获取失败异常
class ProxyGetFailException(BackendException):
    def __init__(self, message: str = '代理加载失败'):
        self.message = message


# 会话创建失败异常
class SessionInitException(BackendException):
    def __init__(self, message: str = '会话创建失败异常'):
        self.message = message


# 接口失败异常
class ApiFailException(BackendException):
    def __init__(self, message: str = '接口调用失败'):
        self.message = message


class OfflineException(Exception):
    """商品下架异常"""
    meta = None

    def __init__(self, meta=None):
        self.meta = meta


class NotExistException(Exception):
    """商品不存在异常"""
    meta = None

    def __init__(self, meta=None):
        self.meta = meta


class NotStockException(Exception):
    """商品无库存异常"""
    meta = None

    def __init__(self, meta=None):
        self.meta = meta


class NotKnownException(Exception):
    """商品未知异常"""
    meta = None

    def __init__(self, meta=None):
        self.meta = meta


class AbandonException(Exception):
    """放弃异常"""
    meta = None

    def __init__(self, meta=None):
        self.meta = meta
