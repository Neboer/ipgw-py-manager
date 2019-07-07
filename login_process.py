import requests
from bs4 import BeautifulSoup
from requests import TooManyRedirects
import getpass
from requestresult import SuccessPage, UnionAuth, Device
from show_result import distinguish_and_build, read_unpw_from_settings, print_login_successful, print_fail_auth


def temp_login(session: requests.Session, username, password):
    # 优先使用cookie登录。如果cookie不行，则会使用用户名密码登录。这个函数只能返回两种结果，要么是密码错误所导致的fail Unionauth，要么是登录成功的界面。main本身不关心具体实现的细节.
    try:
        first_login_response = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    except TooManyRedirects:  # cookie过期，学校会在first反复重定向。
        print("cookies are out of date, login with default username")
        session.cookies.clear()
        first_login_response = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    first_login_result = distinguish_and_build(BeautifulSoup(first_login_response.text, "lxml"))
    if type(first_login_result) is SuccessPage:  # 第一遍就登录进去了。
        if first_login_result.status == 0:
            first_login_result.get_detailed_traffic_and_online_seconds(session)
        return first_login_result
    elif type(first_login_result) is UnionAuth:  # 返回统一认证，说明没有cookie或者cookie被清空。
        auth_login_result = first_login_result.login(username, password, session)
        if type(auth_login_result) is UnionAuth and auth_login_result.last_temp == 5:
            # 出现玄学问题，登录结果并不返回任何错误信息。这个问题的产生和错误的第三段cookie异常很有关系。解决此现象的方法只有一个，清除所有cookie，然后重新登录。
            print("cookies may be modified or too old, login with default username.")
            session.cookies.clear()
            return temp_login(session, username, password)
        else:
            return auth_login_result
    else:
        raise NameError("unknown response")


def whole_process(pass_username: str, session: requests.Session, settings: dict, login: bool):
    if pass_username:  # 如果用户指定了用户名，则用指定的用户名登录
        password = getpass.getpass()
        username = pass_username
    else:
        username, password = read_unpw_from_settings(settings)
    if (not username) or (not password):
        print("username or password is empty, exit.")
        exit(1)
    result = temp_login(session, username, password)
    if type(result) is UnionAuth:
        print_fail_auth(result)
    elif type(result) is SuccessPage:
        if login:
            if result.status == 0:
                result.get_detailed_traffic_and_online_seconds(session)
            other_online_choice = print_login_successful(result)
            if other_online_choice == 2:  # logout and re-login
                Device.logout_sid(result.online_other_uid, session)
                whole_process(pass_username, session, settings, login)
                return 0
            elif other_online_choice == 3:  # just re-login
                whole_process(pass_username, session, settings, login)
                return 0
        else:
            for device in result.device_list:
                if device.logout(session):
                    print("logout {} successful".format(device.sid))
                else:
                    print("logout {} error".format(device.sid))
    else:
        raise NameError("unknown response.")
