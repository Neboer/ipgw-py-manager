# main ipgw progress
from .api.SSO_error import UnionAuthError
from .errors_modals import LoginResult
from .prepare_session import prepare_session
from .api.SSO import SSO_prepare, SSO_login
from .api.portal import login_from_sso, get_info, logout, batch_logout, get_ipgw_session_acid
from .api.portal_error import IPAlreadyOnlineError, OtherException, IPNotOnlineError


# 描述一个ipgw统一身份认证的全过程。
class IPGW:
    # 初始化，获得一个ipgw的统一身份认证界面
    def __init__(self):
        self.sess = prepare_session()
        self.union_auth_page = SSO_prepare(self.sess)
        self.status = None
        self.acid = get_ipgw_session_acid(self.sess)

    def login(self, username, password):
        try:
            token = SSO_login(self.sess, self.union_auth_page, username, password, self.acid)
        except UnionAuthError as e:
            return LoginResult.UsernameOrPasswordError
        result = login_from_sso(self.sess, token, self.acid)
        if result['code'] == 0:
            # 至此，登录已经顺利完成。
            return LoginResult.LoginSuccessful
        elif result['code'] == 1:
            # 用户已经在线了！
            return LoginResult.UserAlreadyOnlineError
        else:
            # 未知报错，暂且报错。
            raise OtherException(result)

    def get_status(self):
        result = get_info(self.sess)
        self.status = result
        return result

    def advanced_logout(self, username, ip_addr):
        result = logout(self.sess, username, ip_addr, self.acid)
        if result['ecode'] == 0:
            pass
        elif result['error_msg'] == "You are not online.":
            raise IPNotOnlineError()
        else:
            raise OtherException(result)

    def batch_logout(self):
        result = batch_logout(self.sess)
        if result['code'] == 1:
            raise IPNotOnlineError()
        elif result['code'] == 0:
            pass
        else:
            raise OtherException(result)
