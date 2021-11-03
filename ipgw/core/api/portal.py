from math import floor
from requests import Session
from time import time
from random import choice
from string import digits
from typing import TypedDict, Union
from json import loads


class IPGWOnlineInfo(TypedDict):
    ServerFlag: int
    add_time: int
    all_bytes: int
    billing_name: str
    bytes_in: int
    bytes_out: int
    checkout_data: int
    domain: str
    error: str
    group_id: str
    keepalive_time: int
    online_device_total: str
    online_ip: str
    online_ip6: str
    package_id: str
    products_id: str
    products_name: str
    real_name: str
    remain_bytes: int
    remain_seconds: int
    sum_bytes: int
    sum_seconds: int
    sysver: str
    user_balance: int
    user_charge: int
    user_mac: str
    user_name: int
    wallet_balance: int


class IPGWNotOnlineInfo(TypedDict):
    client_ip: str
    ecode: int
    error: str
    error_msg: str
    online_ip: str
    res: str
    srun_ver: str
    st: int


# 去掉字符串开头的jQueryxxx({}) -> JSON{}
def _unwrap_javascript_json(text) -> dict:
    start = text.find('{')
    end = text.rfind('}')
    return loads(text[start:end + 1])


def _timestamp():
    return floor(time() * 1000)


def _jq_cbid():
    random_str = ''.join(choice(digits) for _ in range(17))
    return f'jQuery1124{random_str}_{_timestamp()}'


# sso_token:ST-2166499-vqj94U9Dfyliw06sqLLH-tpass
def login_from_sso(session: Session, sso_token):
    return session.get(f"http://ipgw.neu.edu.cn/v1/srun_portal_sso?ac_id=1&ticket={sso_token}",
                       headers={"referer": f"http://ipgw.neu.edu.cn/srun_portal_sso?ac_id=1&ticket={sso_token}"}).json()


def get_info(session: Session) -> Union[IPGWOnlineInfo, IPGWNotOnlineInfo]:
    reply = session.get(
        f"http://ipgw.neu.edu.cn/cgi-bin/rad_user_info?callback=&callback={_jq_cbid()}_{_timestamp()}_={_timestamp()}")
    return _unwrap_javascript_json(reply.text)


def logout(session: Session, username, ip):
    reply = session.get(
        f"http://ipgw.neu.edu.cn/cgi-bin/srun_portal?callback={_jq_cbid()}_{_timestamp()}&action=logout&username={username}&ip={ip}&ac_id=1&_={_timestamp()}"
    )
    return _unwrap_javascript_json(reply.text)


def batch_logout(session: Session):
    reply = session.post("http://ipgw.neu.edu.cn/v1/batch-online-drop")
    return _unwrap_javascript_json(reply.text)
