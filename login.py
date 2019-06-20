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


def login(session: requests.Session, username=None, password=None):
    try:
        login_result_soup = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    except TooManyRedirects:
        print("Cookies are out of date, rebuilding.")
        session.cookies.clear()
        login_result_soup = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    temp_login = distinguish_and_build(BeautifulSoup(login_result_soup.text, "lxml"))
    if type(temp_login) is SuccessPage:
        temp_login.refresh(session)
        return temp_login
    elif type(temp_login) is UnionAuth:
        if username is not None:
            if username != "" and password != "":
                return temp_login.login(username, password, session)
            else:
                print("username or password cannot be empty")
        else:
            return temp_login
    else:
        return None


def print_login_successful(page: SuccessPage):
    if page.online_other_uid:
        print("other online, uid:", page.online_other_uid)
    else:
        print("account: {}\nip: {}\nconsumed: {}\nonline: {}\n".format(page.base_info[0], page.base_info[1],
                                                                       page.base_info[2], page.base_info[3]))
    for device in page.device_list:
        print(device)


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
