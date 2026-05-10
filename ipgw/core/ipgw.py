# main ipgw progress
import logging
from time import sleep
from typing import Callable, Optional, Union

from .api.sso import sso_prepare, sso_login
from .api.sso_error import UnionAuthError
from .api.sso_mobile import MobileSSOLoginApi
from .api.sso_mobile_error import MobileSSOLoginFailedError, MobileSSOTGTExpiredError
from .api.portal import IPGWNotOnlineInfo, IPGWOnlineInfo, login_from_sso, get_info, logout, batch_logout, get_ipgw_session_acid
from .api.portal_error import OtherException, IPNotOnlineError
from .errors_modals import LoginResult
from .prepare_session import prepare_session


# 描述一个ipgw统一身份认证的全过程。
class IPGW:
    # 初始化，获得一个ipgw的统一身份认证界面
    # 在参数中加入bypass_proxy,用以判断是否跳过系统代理
    # mobile=True 时跳过 Web SSO 页面准备，改用手机端 SSO 登录
    def __init__(self, bypass_proxy: bool = False, mobile: bool = False):
        self.sess = prepare_session(bypass_proxy) # 传入bypass_proxy
        self.mobile = mobile
        if not mobile:
            self.union_auth_page = sso_prepare(self.sess)
        self.status: Optional[Union[IPGWOnlineInfo, IPGWNotOnlineInfo]] = None
        self.acid = get_ipgw_session_acid(self.sess)
        logging.debug(f"get_ipgw_session_acid: {self.acid}")

    def login(self, username, password):
        try:
            token = sso_login(self.sess, self.union_auth_page, username, password, self.acid)
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

    def acquire_mobile_tgt(self, username: str, password: str,
                           sms_callback: Optional[Callable[[], str]] = None) -> str:
        """获取手机端 SSO 的 TGT。

        sms_callback 在需要短信验证码时调用，应返回用户输入的验证码字符串。
        返回 TGT 字符串。用户名或密码错误时抛出 MobileSSOLoginFailedError。
        """
        mobile_api = MobileSSOLoginApi(self.sess)

        tgt = mobile_api.request_login(username, password)
        if tgt is None:
            if sms_callback is None:
                raise RuntimeError("需要短信验证码，但未提供 sms_callback")
            mobile_api.send_sms_code(username, password)
            sms_code = sms_callback()
            tgt = mobile_api.submit_sms_code(sms_code)

        logging.debug(f"acquire_mobile_tgt: {tgt}")
        return tgt

    def login_with_mobile_tgt(self, tgt: str) -> LoginResult:
        """用已持有的 TGT 登录 ipgw。

        将 TGT（CASTGC）换成 CAS Service Ticket，再通过 ipgw 的 sso 接口登录。
        """
        mobile_api = MobileSSOLoginApi(self.sess)
        service_url = f"http://ipgw.neu.edu.cn/srun_portal_sso?ac_id={self.acid}"

        try:
            st = mobile_api.exchange_tgt_for_st(tgt, service_url)
        except MobileSSOTGTExpiredError:
            return LoginResult.UsernameOrPasswordError  # TGT 过期，需重新获取

        result = login_from_sso(self.sess, st, self.acid)
        logging.debug(f"mobile login result: {result}")

        if result['code'] == 0 and result['message'] == 'success':
            return LoginResult.LoginSuccessful
        elif result['code'] == 1 and result['message'] == 'E2616: Arrearage users.':
            return LoginResult.ArrearageUserError
        elif result['code'] == 1 and result['message'] == 'no_response_data_error':
            return LoginResult.NoResponseDataError
        else:
            logging.error(f"登录时遇到未知错误：{result['code']}, {result['message']}")
            raise OtherException(result)

    def get_status(self, must_success = False) -> Union[IPGWOnlineInfo, IPGWNotOnlineInfo]:
        max_retries = 5
        result = None
        for _ in range(max_retries):
            result = get_info(self.sess)
            if not must_success:
                break
            elif 'billing_name' in result and len(result['billing_name'].strip()) == 0:
                # IPGW系统的bug，在长时间不登录系统后突然登录可能会无法获得账号信息。
                logging.warning("暂时无法获取账号信息，重试中……")
                sleep(1)
                continue
            else:
                break
        else:
            logging.error("错误：暂时无法获取完整账号信息。")

        if result is None:
            raise OtherException("无法获取账号信息。")

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
