# 打印登录成功的信息
from tabulate import tabulate
from datetime import timedelta

from ..core.api.portal import IPGWOnlineInfo, IPGWNotOnlineInfo
from typing import Union


def _sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1000.0:
            return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1000.0
    return "%.2f%s%s" % (num, 'Yi', suffix)


def print_ipgw_status(info: Union[IPGWOnlineInfo, IPGWNotOnlineInfo]):
    # 结构化输出
    if info['error'] == 'ok':
        total_bytes = info['remain_bytes'] + info['sum_bytes']
        sum_bytes = info['sum_bytes']
        try:
            percentage = f"{(sum_bytes*100 / total_bytes):.3}%"
        except ZeroDivisionError:
            percentage = "N/A%"
        info_table = [
            ['登录帐号', info['user_name']],
            ['IP地址', info['online_ip']],
            ['套餐名称', info['billing_name']],
            ['本次流量', f"下行{_sizeof_fmt(info['bytes_in'])} 上行{_sizeof_fmt(info['bytes_out'])}"],
            ['总流量使用', f"{_sizeof_fmt(sum_bytes)} / {_sizeof_fmt(total_bytes)} 已用{percentage}"],
            ['在线时长', str(timedelta(seconds=info['sum_seconds']))]
        ]
        print(tabulate(info_table, tablefmt='simple'))
    elif info['error'] == 'not_online_error':
        print(f'IP地址{info["client_ip"]}目前没有在线。')
