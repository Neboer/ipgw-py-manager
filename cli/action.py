from args import args
from core.errors_modals import *
from core.config import User, config, add_user, query_user_by_username, query_default_user, set_default_username, \
    update_last_login_info
from getpass import getpass
from datetime import timedelta
import logging
from tabulate import tabulate

from core.ipgw import IPGW

logging.basicConfig(format='%(message)s', level=logging.INFO)

# 程序第0步：如果需要设置默认登录用户，那么就设置。
if args.action == 'default':
    set_default_username(args.username)

# 程序第一步：根据命令行生成需要使用的用户名和密码，查明用户想要的下线模式。
target_user: User = {}
target_sid: str = args.sid if args.sid else None  # 如果用户指定了sid，那么这就是目标。如果用户没有指定，但是指定了last，那配置文件里记载的sid就是目标。
kick_action = args.kick if args.kick else config["default_kick"]

if args.last:
    # 如果程序指定了last选项，那么假装用户输入了对应的最后信息。
    args.username = config['last_login_username']
    args.sid = config['last_sid']

if not args.username:
    # 如果没有指定用户名，则使用默认用户身份。
    target_user = query_default_user()
else:
    # 程序指定了用户名，先查询是否有此用户的密码。
    target_user["username"] = args.username
    if args.password:
        target_user["password"] = args.password
    else:
        # 如果用户没有提供用户名，先看看配置文件里有没有保存用户。
        t = query_user_by_username(args.username)
        if t:  # 如果找到了
            target_user = t
        else:  # 如果没找到，请用户输入。
            target_user["password"] = getpass('输入密码：')
# 经过这番折腾，应该有用户名和密码了。

if args.action == 'add':  # 先来做一些离线的事情
    add_user(target_user)
    logging.info("添加成功")
    exit(0)

# 接下来，需要处理网络登录登出问题了。
main_ipgw = IPGW()
if args.sid:  # 如果用户指定了sid，那么用户一定是想下线这个设备。我们不如先尝试下线一下用户的这个设备，如果成功就ok了。
    try:
        main_ipgw.logout(args.sid)
    except RequestNeedCASAuthenticError:  # 用户需要认证
        pass
    else:
        # 如果用户直接下线成功……
        logging.info("快速下线成功！")
        exit(0)  # 直接退出程序。


def ipgw_main_login():
    main_ipgw.login(target_user['username'], target_user['password'])


while True:
    ipgw_main_login()
    # 打印登录状态
    current_ipgw_status = main_ipgw.get_ipgw_status()

    if current_ipgw_status == PageStatus.Normal:
        def sizeof_fmt(num, suffix='B'):
            for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
                if abs(num) < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, 'Yi', suffix)


        base_info = main_ipgw.success_page.base_info
        # 结构化输出
        info_table = [
            ['登录帐号', base_info['student_number']],
            ['IP地址', base_info['ip']],
            ['已用流量', sizeof_fmt(base_info['consume_bytes'])],
            ['在线时长', str(timedelta(seconds=base_info['online_time_sec']))]
        ]
        devices_table_header = ['当前', 'IP地址', '登录时间', '在线时长', '已用流量']
        devices_table = [
            [
                '*' if cd.is_current else ' ',
                cd.ip,
                cd.login_date,
                cd.duration,
                cd.flow
            ]
            for cd in main_ipgw.success_page.device_list
        ]
        print(tabulate(info_table, tablefmt='simple'))
        print(tabulate(devices_table, headers=devices_table_header))
        break

    elif current_ipgw_status == PageStatus.OtherDeviceOnline:
        # 有其他设备在线！看看kick方法是怎么定义的行为？
        if kick_action == 'relogin':
            # 下线这个同学，然后重新登录。
            main_ipgw.logout_online_others()
            continue
        elif kick_action == 'logout':
            # 只是简单登出这个人，并不再登录了。不再登录意味着无法进行后面的任何行为。
            main_ipgw.logout_online_others()
            exit(0)
        elif kick_action == 'exit':
            # 不做任何处理
            exit(0)

    elif current_ipgw_status == PageStatus.ServiceDisabled:
        logging.error('用户已经暂停服务。')
        exit(-2)
    elif current_ipgw_status == PageStatus.InsufficientFee:
        logging.error('此账号余额不足月租，无法继续使用。')
        exit(-1)

if args.action == 'login':  # 用户只是希望登录，那么一切都结束了。
    # 将用户信息写入配置文件。
    update_last_login_info(main_ipgw.success_page.base_info['student_number'],
                           main_ipgw.get_current_device().sid)
    exit(0)
if args.action == 'logout':  # 用户登出，快捷登出没有成功，或者用户想要进行高级登出。
    logout_all_devices = not args.self and not args.only  # 既没有self又没有only，即可快速logout。
    main_ipgw.advanced_logout(only_keep_self=args.only, only_logout_self=args.self,
                              logout_all_devices=logout_all_devices)
    if args.self:
        logging.info("自我下线。")
    elif args.only:
        logging.info("仅保留自己在线。")
    elif logout_all_devices:
        logging.info("已经全部下线。")
    exit(0)
