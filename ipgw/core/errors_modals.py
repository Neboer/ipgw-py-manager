from enum import Enum
from typing import TypedDict

ua = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'''
# target = '''https://pass.neu.edu.cn/tpass/login?service=https%3A%2F%2Fipgw.neu.edu.cn%2Fsrun_cas.php%3Fac_id%3D1'''
target = '''https://pass.neu.edu.cn/tpass/login?service=http%3A%2F%2Fipgw.neu.edu.cn%2Fsrun_portal_sso%3Fac_id%3D1'''

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


class NoDefaultUserError(Exception):  # 没有找到默认用户的错误
    pass


class UsernameOrPasswordEmptyError(Exception):  # 用户名或者密码为空错误。
    pass


class UsernameNotInConfigFileError(Exception):  # 配置文件中查询不到提供的用户名，命令行中也没有提供密码，因此无法登录。
    pass


class EmptyLastLoginInfoError(Exception):  # 有关上次登录的信息为空，而用户却又请求使用上次登录的结果。
    pass


class NoCurrentDeviceError(Exception):  # 没有当前刚刚登录的设备信息。
    pass


class PageTitle:
    UnionAuth = "智慧东大--统一身份认证"
    SystemHint = "系统提示"
    EmailVerification = "智慧东大"  # 出现这个标题意味着用户需要进行邮箱认证
    SuccessPage = "IP控制网关"


class LoginResult(Enum):
    LoginSuccessful = 0
    UsernameOrPasswordError = 1
    AttemptReachLimit = 2
    UserAlreadyOnlineError = 3
    ArrearageUserError = 4 # 用户已欠费


# SuccessPage的两个依赖
class PageStatus(Enum):
    Normal = 0
    ServiceDisabled = 1
    InsufficientFee = 2
    OtherDeviceOnline = 3
    Unknown = -1


class BaseInfo(TypedDict):
    student_number: str
    ip: str
    consume_bytes: int  # 已用流量
    online_time_sec: int  # 总在线时长
