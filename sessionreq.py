import requests, re
from bs4 import BeautifulSoup, Tag


def bake_cookie(cname, cvalue, until):
    build_cookie = {cname: cvalue, "expires": until}
    return build_cookie


def pass_authenticate(username, password, session: requests.Session):
    r = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    soup = BeautifulSoup(r.text, 'lxml')
    form: Tag = soup.find("form", {'id': 'loginForm'})
    destination = form.attrs['action']
    ext_lt_string = form.find("input", {'id': 'lt'}).attrs["value"]
    execution = form.find("input", {'name': 'execution'}).attrs["value"]
    formData = {
        'rsa': username + password + ext_lt_string,
        'ul': len(username),
        'pl': len(password),
        'lt': ext_lt_string,
        'execution': execution,
        '_eventId': 'submit'
    }
    return session.post("https://pass.neu.edu.cn" + destination, data=formData)


def login_fail(login_result: str):
    if login_result.find("智慧东大--统一身份认证") != -1:
        last_number = re.search("连续登录失败5次，账号将被锁定1分钟，剩余次数(.)", login_result)
        if last_number:
            return int(last_number.group(1))
        else:
            return -1  # 连续登录失败，ip将停止使用1分钟。
    else:
        if login_result.find("访问被拒绝") != -1:
            return -1  # 连续登录失败，ip将停止使用1分钟。
        return None  # 代表登录成功


def connect_to_ipgw_by_unpw(username: str, password: str, setting_data: dict, connect_session: requests.Session = None):
    if not connect_session:
        connect_session = requests.session()
    connect_session.headers.update(setting_data["global_headers"])
    requests.utils.cookiejar_from_dict(setting_data["ipgw_cookie_jar"], connect_session.cookies)
    connect_session.get('http://ipgw.neu.edu.cn/srun_portal_pc.php?ac_id=1&')
    pass_login_result = pass_authenticate(username, password, connect_session).text  # 调试用账号密码 TODO:增加登录失败的提示
    ifLoginFailLastTryTime = login_fail(pass_login_result)
    if ifLoginFailLastTryTime is None:
        pass_online_info = connect_session.get(
            "https://ipgw.neu.edu.cn/srun_cas.php?ac_id=1").text  # 如果登陆成功，重新访问在线信息列表，以获得最新的状态数据。
        setting_data["ipgw_cookie_jar"].update(requests.utils.dict_from_cookiejar(connect_session.cookies))
        return pass_online_info
    else:
        setting_data["ipgw_cookie_jar"].update(requests.utils.dict_from_cookiejar(connect_session.cookies))
        return ifLoginFailLastTryTime
    # with open("resources/union_fail.html","w") as file:
    #     file.write(pass_login_result)

    # print(parse_online_data(pass_login_result))
