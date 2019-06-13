from bs4 import BeautifulSoup, Tag
import requests
import re


class Device:
    ip = ""
    login_date = ""
    duration = ""
    flow = ""
    is_current = False
    uid = 0

    def logout(self, session: requests.Session):
        data = {'action': 'dm', 'sid': self.uid}
        session.post('https://ipgw.neu.edu.cn/srun_cas.php', data=data)

    def __init__(self, ip, login_date, duration, flow):
        self.ip = ip
        self.login_date = login_date
        self.duration = duration
        self.flow = flow


with open("out.html", "r") as online_data:
    online_data_soup = BeautifulSoup(online_data.read(), 'html.parser')
    device_info_soup: Tag = online_data_soup.find("table", {'class': 'table'})
    device_soup_array: [Tag] = device_info_soup.find_all("tr", {'id': 'tr_'})
    device_info = []
    for single_device_soup in device_soup_array:  # type: Tag
        piece_info_array = single_device_soup.text.splitlines()
        current_device = Device(piece_info_array[1], piece_info_array[2], piece_info_array[3], piece_info_array[4])
        current_device.uid = re.search("do_drop\(\'(.*)\'\)", str(single_device_soup)).group(1)
        if "style" in single_device_soup.attrs:
            current_device.is_current = True
        device_info.append(current_device)
