import requests
from bs4 import BeautifulSoup
from requestresult import SuccessPage, UnionAuth
from datetime import timedelta


def distinguish_and_build(page_soup: BeautifulSoup):
    title = page_soup.find("title").text
    if title == "系统提示" or title == "智慧东大--统一身份认证":
        return UnionAuth(page_soup)
    elif title == "IP控制网关":
        return SuccessPage(page_soup)
    else:
        return None


def print_login_successful(page: SuccessPage):
    if page.status == 0:
        if page.online_other_uid:
            print("other online, uid:", page.online_other_uid)
        else:
            if page.base_info[2] <= 1e6:
                print_number = page.base_info[2] / 1000
                flow_format = "{:d}K"
            else:
                print_number = page.base_info[2] / 1e6
                flow_format = "{:.2f}M"
            online_time = timedelta(seconds=page.base_info[3])
            print(("account: {}\nip: {}\nconsumed: " + flow_format + "\nonline_time: {}\n").format(page.base_info[0],
                                                                                                   page.base_info[1],
                                                                                                   print_number,
                                                                                                   str(online_time)))
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
