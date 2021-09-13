# 打印登录成功的信息
from ..core.requestresult import SuccessPage
from tabulate import tabulate
from datetime import timedelta


def _sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def print_ipgw_status(success_page: SuccessPage):
    base_info = success_page.base_info
    # 结构化输出
    info_table = [
        ['登录帐号', base_info['student_number']],
        ['IP地址', base_info['ip']],
        ['已用流量', _sizeof_fmt(base_info['consume_bytes'])],
        ['在线时长', str(timedelta(seconds=base_info['online_time_sec']))]
    ]
    devices_table_header = ['当前', 'sid', 'IP地址', '登录时间', '在线时长', '已用流量']
    devices_table = [
        [
            '*' if cd.is_current else ' ',
            cd.sid,
            cd.ip,
            cd.login_date,
            cd.duration,
            cd.flow
        ]
        for cd in success_page.device_list
    ]
    print(tabulate(info_table, tablefmt='simple'))
    print(tabulate(devices_table, headers=devices_table_header))
