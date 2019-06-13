import requests
from bs4 import BeautifulSoup, Tag
from parse_account_online_data import parse_online_data


def bake_cookie(cname, cvalue, until):
    build_cookie = {cname: cvalue, "expires": until}
    return build_cookie


def pass_authenticate(username, password, session: requests.Session):
    r = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    with open("out.html","w") as out:
        out.write(r.text)
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


connect_session = requests.Session()
connect_session.headers.update({'User-Agent':
                                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
                                "Origin": "https://pass.neu.edu.cn",
                                "Referer": "https://pass.neu.edu.cn/tpass/login?service=https%3A%2F%2Fipgw.neu.edu.cn%2Fsrun_cas.php%3Fac_id%3D3",
                                "Upgrade-Insecure-Requests": "1",
                                "Host": "pass.neu.edu.cn"
                                })
connect_session.get('http://ipgw.neu.edu.cn/srun_portal_pc.php?ac_id=1&')
count = open("resources/count", "r").readlines()
pass_login_result = pass_authenticate(count[0][:-1], count[1], connect_session).text  # 调试用账号密码 TODO:增加登录失败的提示
pass_online_info = connect_session.get("https://ipgw.neu.edu.cn/srun_cas.php?ac_id=1").text  # 如果登陆成功，重新访问在线信息列表，以获得最新的状态数据。
online_data = parse_online_data(pass_online_info)
print(online_data[0])
for device in online_data:
    device.logout(connect_session)

# print(parse_online_data(pass_login_result))