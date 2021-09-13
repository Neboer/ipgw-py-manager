import requests, re
from bs4 import BeautifulSoup, Tag
from .errors_modals import *
import logging

logger = logging.getLogger(__name__)

# 描述一个连接到网络上的设备。
class Device:
    @staticmethod
    def logout_sid(sid: str, session: requests.Session):
        logout_result = session.post('https://ipgw.neu.edu.cn/srun_cas.php', data={'action': 'dm', 'sid': sid}).text
        if logout_result == "下线请求已发送":
            return
        else:
            if logout_result.find("CAS Authentication wanted!"):
                raise RequestNeedCASAuthenticError
            else:
                raise UnknownPageError(logout_result)

    # 在解析的时候，能够从tr标签直接自我实例化。
    @staticmethod
    def init_from_tr(tr: Tag):
        piece_info_array = tr.text.splitlines()
        sid = re.search("do_drop\\(\'(.*)\'\\)", str(tr)).group(1)
        is_current = "style" in tr.attrs
        return Device(*piece_info_array[1:5], is_current, sid)

    def logout(self, session: requests.Session):
        return self.logout_sid(self.sid, session)

    def __init__(self, ip, login_date, duration, flow, is_current, sid):
        self.ip = ip
        self.login_date = login_date
        self.duration = duration  # 已在线时长
        self.flow = flow  # 已用流量
        self.is_current = is_current
        self.sid = sid


class SuccessPage:
    # 这个parse_status和parse_base_info都是直接改变对象值的函数，在实例化的时候调用即可。
    def parse_status(self, success_soup: BeautifulSoup) -> None:
        # 是否有其他用户在线？
        others_online_button: Tag = success_soup.find("a", {"class": "btn btn-block btn-dark"})
        sufficient_fee_hint: Tag = success_soup.find("label", {"class": "fl-label", "style": "color:red;"})

        if others_online_button:
            self.online_other_uid = re.search("do_drop\\('(.*)'\\)", others_online_button.attrs["onclick"]).group(1)
            self.status = PageStatus.OtherDeviceOnline
            return
        # 是否欠费了？或者是否被用户禁用了？
        elif sufficient_fee_hint:
            if sufficient_fee_hint.text.find('余额不足月租，无法使用！') > -1:
                self.status = PageStatus.InsufficientFee
            elif sufficient_fee_hint.text.find('User is disabled'):
                self.status = PageStatus.ServiceDisabled
            return
        else:
            self.status = PageStatus.Normal

    def get_detailed_traffic_and_online_seconds(self, session: requests.Session):
        import random
        key = random.random() * (100000 + 1)
        data = {"action": "get_online_info", "key": key}
        mixed_data_text = session.post("https://ipgw.neu.edu.cn/include/auth_action.php?k=" + str(key),
                                       data=data).text
        if mixed_data_text == 'not online':
            raise UserNotOnlineError
        mixed_data = mixed_data_text.split(',')
        self.base_info['consume_bytes'] = int(mixed_data[0])  # consumed_traffic_bytes
        self.base_info['online_time_sec'] = int(mixed_data[1])  # online_time_seconds

    def parse_base_info(self, success_soup: BeautifulSoup):
        info_soup = success_soup.find("form", {"method": "post", "id": "fm1"}, class_="fm-v")  # type: Tag
        info = tuple(info_soup.stripped_strings)
        self.base_info['student_number'] = info[1]
        self.base_info['ip'] = info[3]

    def parse_devices_list(self, success_soup: BeautifulSoup):
        device_info_soup: Tag = success_soup.find("table", {'class': 'table'})
        device_soup_array: [Tag] = device_info_soup.find_all("tr", {'id': 'tr_'})
        self.device_list: [Device] = [Device.init_from_tr(tr_device_tag) for tr_device_tag in device_soup_array]

    def logout_other(self, session: requests.Session):
        return Device.logout_sid(self.online_other_uid, session)

    def __init__(self, soup: BeautifulSoup):
        self.online_other_uid = None
        self.base_info: BaseInfo = {
            "student_number": '',
            "ip": '',
            "consume_bytes": 0,
            "online_time_sec": 0
        }
        self.device_list = []
        self.status = PageStatus.Unknown
        self.parse_status(soup)
        # 如果状态正常，则正常解析基本信息。
        if self.status == PageStatus.Normal:
            self.parse_base_info(soup)
        self.parse_devices_list(soup)


class UnionAuth:  # 代表一个统一认证页面。
    def __init__(self, soup: BeautifulSoup):
        form: Tag = soup.find("form", {'id': 'loginForm'})
        self.form_destination = form.attrs['action']
        self.form_lt_string = form.find("input", {'id': 'lt'}).attrs["value"]
        self.form_execution = form.find("input", {'name': 'execution'}).attrs["value"]

    def login(self, username, password, session: requests.Session):
        form_data = {
            'rsa': username + password + self.form_lt_string,
            'ul': len(username),
            'pl': len(password),
            'lt': self.form_lt_string,
            'execution': self.form_execution,
            '_eventId': 'submit'
        }
        login_result = session.post("https://pass.neu.edu.cn" + self.form_destination, data=form_data)
        login_result_soup = BeautifulSoup(login_result.text, "lxml")
        response_page_title = login_result_soup.find("title").text
        if response_page_title == PageTitle.UnionAuth:
            raise UnionAuthError()
        elif response_page_title == PageTitle.EmailVerification:
            # 这个页面可能会出现，因为目标未绑定邮箱。我们这里的处理方法就是简单跳过。
            logging.warning("帐号未绑定邮箱")
            login_result_soup = BeautifulSoup(session.get('https://ipgw.neu.edu.cn/srun_cas.php?ac_id=1').text, "lxml")
            return SuccessPage(login_result_soup)
        elif response_page_title == PageTitle.SuccessPage:
            # 登录成功！
            return SuccessPage(login_result_soup)
        else:
            raise UnknownPageError(login_result_soup)
