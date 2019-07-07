import requests, re
from bs4 import BeautifulSoup, Tag


class UnionAuth:  # 代表一个统一认证页面。
    last_temp = 5
    locked = False
    form_lt_string = None
    form_destination = None
    form_execution = None

    def __init__(self, soup: BeautifulSoup):
        if soup.find("title").text == "智慧东大--统一身份认证":
            fail_info: Tag = soup.find("span", {"id": "errormsghide"})
            if fail_info:
                self.last_temp = int(fail_info.text[-1])
            form: Tag = soup.find("form", {'id': 'loginForm'})
            self.form_destination = form.attrs['action']
            self.form_lt_string = form.find("input", {'id': 'lt'}).attrs["value"]
            self.form_execution = form.find("input", {'name': 'execution'}).attrs["value"]
        else:
            self.locked = True

    def login(self, username, password, session: requests.Session):
        form_data = {
            'rsa': username + password + self.form_lt_string,
            'ul': len(username),
            'pl': len(password),
            'lt': self.form_lt_string,
            'execution': self.form_execution,
            '_eventId': 'submit'
        }
        login_result = session.post("https://pass.neu.edu.cn" + self.form_destination, data=form_data).text
        soup = BeautifulSoup(login_result, "lxml")
        import show_result
        result_page = show_result.distinguish_and_build(soup)
        return result_page


class Device:
    ip = ""
    login_date = ""
    duration = ""
    flow = ""
    is_current = False
    sid = "0"

    @staticmethod
    def logout_sid(sid: str, session: requests.Session) -> bool:
        logout_result = session.post('https://ipgw.neu.edu.cn/srun_cas.php', data={'action': 'dm', 'sid': sid}).text
        if logout_result == "下线请求已发送":
            return True
        else:
            if logout_result.find("CAS Authentication wanted!"):
                return False
            else:
                print("other response received when logout:\n", logout_result)
                return False

    def logout(self, session: requests.Session):
        return self.logout_sid(self.sid, session)

    def __init__(self, ip, login_date, duration, flow):
        self.ip = ip
        self.login_date = login_date
        self.duration = duration
        self.flow = flow

    def __str__(self):
        current = ''
        if self.is_current:
            current = "current"
        return self.ip + ' ' + "login date: " + self.login_date + ' ' + "duration: " + \
               self.duration + ' ' + "consume: " + self.flow + ' ' + current + ' uid: ' + str(self.sid)


class SuccessPage:
    online_other_uid = None
    base_info = []
    device_list = []
    status = 0  # 0正常 1关闭服务 2欠费 3其他设备在线

    def parse_status(self, success_soup: BeautifulSoup):
        other_soup: Tag = success_soup.find("a", {"class": "btn btn-block btn-dark"})
        if other_soup:
            self.online_other_uid = re.search("do_drop\\('(.*)'\\)", other_soup.attrs["onclick"]).group(1)
            self.status = 3
            return 3
        sufficient_soup: Tag = success_soup.find("label", {"class": "fl-label", "style": "color:red;"})
        if sufficient_soup:
            self.status = 2
            return 2
        return 0

    def get_detailed_traffic_and_online_seconds(self, session: requests.Session):
        import random
        key = random.random() * (100000 + 1)
        data = {"action": "get_online_info", "key": key}
        mixed_data = session.post("https://ipgw.neu.edu.cn/include/auth_action.php?k=" + str(key),
                                  data=data).text.split(",")
        self.base_info[2] = int(mixed_data[0])  # consumed_traffic_bytes
        self.base_info[3] = int(mixed_data[1])  # online_time_seconds

    def parse_base_info(self, success_soup: BeautifulSoup):
        info_soup = success_soup.find("form", {"method": "post", "id": "fm1"}, class_="fm-v")  # type: Tag
        info = tuple(info_soup.stripped_strings)
        self.base_info = [info[1], info[3], None, None]

    def parse_devices_list(self, success_soup: BeautifulSoup):
        self.device_list.clear()
        device_info_soup: Tag = success_soup.find("table", {'class': 'table'})
        device_soup_array: [Tag] = device_info_soup.find_all("tr", {'id': 'tr_'})
        for single_device_soup in device_soup_array:  # type: Tag
            piece_info_array = single_device_soup.text.splitlines()
            current_device = Device(piece_info_array[1], piece_info_array[2], piece_info_array[3], piece_info_array[4])
            current_device.sid = re.search("do_drop\\(\'(.*)\'\\)", str(single_device_soup)).group(1)
            if "style" in single_device_soup.attrs:
                current_device.is_current = True
            self.device_list.append(current_device)

    def logout_other(self, session: requests.Session):
        return Device.logout_sid(self.online_other_uid, session)

    def __init__(self, soup: BeautifulSoup):
        if self.parse_status(soup) == 0:
            self.parse_base_info(soup)
        self.parse_devices_list(soup)
