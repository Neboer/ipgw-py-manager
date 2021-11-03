# 东北大学修改了统一身份认证登录的逻辑，不再限制过多的登录次数限制。
class UnionAuthError(Exception):
    pass


# 抱歉！您的请求出现了异常，请稍后再试。
class SystemHintError(Exception):
    pass


# 明确且已知的后端错误，比如 Uncaught exception 'RedisException' with message 'read error on connection'之类的东西
class BackendError(Exception):
    def __init__(self, page):
        self.page = page


class UnknownPageError(Exception):
    def __init__(self, page):
        self.page = page


# 在尝试登录之后，页面返回智慧东大，但是并没有提示密码错误次数的信息，这种奇怪的错误在这里报告。
class IntimateUnionAuthPageError(UnknownPageError):
    def __init__(self, page):
        self.page = page


# 登出指定设备需要CAS验证。
class RequestNeedCASAuthenticError(Exception):
    pass


# 在查询用户已经消费的流量或在线时长的时候，服务器返回not online错误。
class UserNotOnlineError(Exception):
    pass