# main ipgw progress
import logging
from time import sleep

from .api.SSO import SSO_prepare, SSO_login
from .api.SSO_error import UnionAuthError
from .api.portal import login_from_sso, get_info, logout, batch_logout, get_ipgw_session_acid
from .api.portal_error import OtherException, IPNotOnlineError
from .errors_modals import LoginResult
from .prepare_session import prepare_session


# 描述一个ipgw统一身份认证的全过程。
class IPGW:
    # 初始化，获得一个ipgw的统一身份认证界面
    def __init__(self):
        self.sess = prepare_session()
        self.union_auth_page = SSO_prepare(self.sess)
        self.status = None
        self.acid = get_ipgw_session_acid(self.sess)
        logging.debug(f"get_ipgw_session_acid: {self.acid}")

    def login(self, username, password):
        try:
            token = SSO_login(self.sess, self.union_auth_page, username, password, self.acid)
            logging.debug(f"sso_login get token: {token}")
        except UnionAuthError:
            return LoginResult.UsernameOrPasswordError
        result = login_from_sso(self.sess, token, self.acid)
        logging.debug(f"sso_login result: {result}")
        # code message: 
        # 0 "success" 登录成功
        # 1 "E2616: Arrearage users." 用户已欠费
        # 1 "message': 'no_response_data_error"
        if result['code'] == 0 and result['message'] == 'success':
            # 至此，登录已经顺利完成。
            return LoginResult.LoginSuccessful
        elif result['code'] == 1 and result['message'] == 'E2616: Arrearage users.':
            # 用户已欠费！
            return LoginResult.ArrearageUserError
        elif result['code'] == 1 and result['message'] == 'no_response_data_error':
            # 用户账号欠费，补交费用后没有重新连接无线网
            return LoginResult.NoResponseDataError
        else:
            # 程序无法解析此错误，说明程序出错。
            logging.error(f"登录时遇到未知错误：{result['code']}, {result['message']}")
            raise OtherException(result)

    def get_status(self, must_success = False):
        max_retries = 5
        result = None
        for i in range(max_retries):
            result = get_info(self.sess)
            if not must_success:
                break
            elif len(result['billing_name'].strip()) == 0:
                # IPGW系统的bug，在长时间不登录系统后突然登录可能会无法获得账号信息。
                logging.warning("暂时无法获取账号信息，重试中……")
                sleep(1)
                continue
            else:
                break
        else:
            logging.error("错误：暂时无法获取完整账号信息。")
        self.status = result
        return result

    def advanced_logout(self, username, ip_addr):
        result = logout(self.sess, username, ip_addr, self.acid)
        logging.debug(f"logout result: {result}")
        if result['ecode'] == 0:
            pass
        elif result['error_msg'] == "你没有在线。":
            raise IPNotOnlineError()
        else:
            raise OtherException(result)

    def batch_logout(self):
        result = batch_logout(self.sess)
        logging.debug(f"batch_logout result: {result}")
        if result['code'] == 1:
            raise IPNotOnlineError()
        elif result['code'] == 0:
            pass
        else:
            raise OtherException(result)
