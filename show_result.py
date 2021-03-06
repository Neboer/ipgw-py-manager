import requests
from bs4 import BeautifulSoup
from requestresult import SuccessPage, UnionAuth, Device


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
        if page.base_info[2] <= 1e6:
            print_number = page.base_info[2] / 1000
            flow_format = "{:d}K"
        else:
            print_number = page.base_info[2] / 1e6
            flow_format = "{:.2f}M"
        # There would be a timedelta module function to convert seconds to time.
        # But however, the result contains days and weeks ... annoying, so I write code below.
        # Convert online seconds to real time, code from GeeksforGeeks.com.
        min, sec = divmod(page.base_info[3], 60)
        hour, min = divmod(min, 60)
        online_time = "{}:{:02d}:{:02d}".format(hour, min, sec)
        print(("account: {}\nip: {}\nconsumed: " + flow_format + "\nonline_time: {}\n").format(page.base_info[0],page.base_info[1],print_number,online_time))
    elif page.status == 1:
        print("account locked, unlock first.")
    elif page.status == 2:
        print("insufficient funds.")
    elif page.status == 3:
        print(
            "other account {} is online. This is usually caused by your online devices. If so, input r to run again and check if the message is shown another time.".format(page.online_other_uid))
        input_option = input("Logout it and re-login? Default reload(y,n,r):")
        if input_option == 'y':
            return 2  # 2: logout and re-login
        elif input_option == 'n':
            for device in page.device_list:
                print(device)
            return 1  # 1: no more action
        elif input_option == 'r' or input_option == '':
            return 3  # 3: re-login
        else:
            raise TypeError("Error input!")
    for device in page.device_list:
        print(device)
    return 0  # normal operation


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
