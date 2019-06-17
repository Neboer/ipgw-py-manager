from bs4 import BeautifulSoup, Tag
import re, requests


def drop_device(uid, session=None):
    if not session:
        session = requests.session()
    data = {'action': 'dm', 'sid': uid}
    session.post('https://ipgw.neu.edu.cn/srun_cas.php', data=data)


class Device:
    ip = ""
    login_date = ""
    duration = ""
    flow = ""
    is_current = False
    uid = 0

    def logout(self, session: requests.Session):
        drop_device(self.uid, session)

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
               self.duration + ' ' + "consume: " + self.flow + ' ' + current + ' uid: ' + str(self.uid)


def parse_login_result(login_res: str):
    return BeautifulSoup(login_res, 'lxml')


def get_devices_data(online_data_soup: BeautifulSoup) -> [Device]:
    device_info_soup: Tag = online_data_soup.find("table", {'class': 'table'})
    device_soup_array: [Tag] = device_info_soup.find_all("tr", {'id': 'tr_'})
    device_info = []
    for single_device_soup in device_soup_array:  # type: Tag
        piece_info_array = single_device_soup.text.splitlines()
        current_device = Device(piece_info_array[1], piece_info_array[2], piece_info_array[3], piece_info_array[4])
        current_device.uid = re.search("do_drop\\(\'(.*)\'\\)", str(single_device_soup)).group(1)
        if "style" in single_device_soup.attrs:
            current_device.is_current = True
        device_info.append(current_device)
    return device_info


def other_account(online_data: str):
    if online_data.find("帮他下线") > -1:
        return re.search("class=\"btn btn-block btn-dark\".*do_drop\\(\'(.*)\'\\)", online_data).group(1)
    else:
        return None


def base_info(online_data_soup: BeautifulSoup):
    info_soup = online_data_soup.find("form", {"method": "post", "id": "fm1"}, class_="fm-v")  # type: Tag
    info = tuple(info_soup.stripped_strings)
    return info[1], info[3], info[5], info[7]
