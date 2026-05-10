from typing import Optional


class MobileSSOStateError(Exception):
    """当前状态不允许此操作。"""
    pass


class MobileSSOLoginFailedError(Exception):
    """服务端明确拒绝登录（如密码错误）。"""
    pass


class MobileSSORequestFailedError(Exception):
    """HTTP 请求或响应解析失败。"""
    def __init__(self, msg: str, code: Optional[int] = None):
        self.msg = msg
        self.code = code


class MobileSSOTGTExpiredError(Exception):
    """CASTGC（TGT）已过期，需要重新登录。"""
    pass
