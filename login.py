import requests
from requests import TooManyRedirects
from bs4 import BeautifulSoup
from requestresult import SuccessPage, UnionAuth


def distinguish_and_build(page_soup: BeautifulSoup):
    title = page_soup.find("title").text
    if title == "系统提示" or title == "智慧东大--统一身份认证":
        return UnionAuth(page_soup)
    elif title == "IP控制网关":
        return SuccessPage(page_soup)
    else:
        return None


def login(session: requests.Session, username, password):
    # 优先使用cookie登录。如果cookie不行，则会使用用户名密码登录。这个函数只能返回两种结果，要么是密码错误所导致的fail Unionauth，要么是登录成功的界面。main本身不关心具体实现的细节.
    try:
        first_login_response = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    except TooManyRedirects:  # cookie过期，学校会在first反复重定向。
        print("cookies are out of date, login with default username")
        session.cookies.clear()
        first_login_response = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    first_login_result = distinguish_and_build(BeautifulSoup(first_login_response.text, "lxml"))
    if type(first_login_result) is SuccessPage:  # 第一遍就登录进去了。
        first_login_result.refresh(session)
        return first_login_result
    elif type(first_login_result) is UnionAuth:  # 返回统一认证，说明没有cookie或者cookie被清空。
        auth_login_result = first_login_result.login(username, password, session)
        if type(auth_login_result) is UnionAuth and auth_login_result.last_temp == 5:
            # 出现玄学问题，登录结果并不返回任何错误信息。这个问题的产生和错误的第三段cookie异常很有关系。解决此现象的方法只有一个，清除所有cookie，然后重新登录。
            print("cookies may be modified, login with default username.")
            session.cookies.clear()
            return login(session, username, password)
        else:
            return auth_login_result
    else:
        raise NameError("unknown response")


def print_login_successful(page: SuccessPage):
    if page.status == 0:
        if page.online_other_uid:
            print("other online, uid:", page.online_other_uid)
        else:
            print("account: {}\nip: {}\nconsumed: {}\nonline: {}\n".format(page.base_info[0], page.base_info[1],
                                                                       page.base_info[2], page.base_info[3]))
        for device in page.device_list:
            print(device)
    elif page.status == 1:
        print("account locked, unlock first.")
    elif page.status == 2:
        print("insufficient funds.")


def print_fail_auth(page: UnionAuth):
    if page.locked:
        print("fail 5 times, account locked for 1 min.")
        return
    print("username or password error, last try {} times.".format(page.last_temp))


def read_settings_into_session(settings, session: requests.Session, set_cookie: bool,
                               set_headers: bool = True):
    cookie_dict = settings["ipgw_cookie_jar"]
    header_dict = settings["global_headers"]
    if set_cookie:
        requests.utils.cookiejar_from_dict(cookie_dict, session.cookies)
    session.headers.update(header_dict)


def read_unpw_from_settings(settings: dict):
    return settings["unity_login"]["username"], settings["unity_login"]["password"]
