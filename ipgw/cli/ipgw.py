from .arguments import args
from ..core.errors_modals import *
from ..core.config import User, config, add_user, query_user_by_username, query_default_user, set_default_username, \
    update_last_login_info
from .get_info import get_settings
from .print_status import print_ipgw_status
import logging

from ..core.ipgw import IPGW

logging.basicConfig(format='%(message)s', level=logging.INFO)


def main():
    # 程序第0步：如果需要设置默认登录用户，那么就设置。
    if args.action == 'default':
        set_default_username(args.username)
        exit(0)

    # 程序第一步：根据命令行生成需要使用的用户名和密码，查明用户想要的下线模式等。
    try:
        target_user, target_sid, kick_action = get_settings()
    except NoDefaultUserError:
        logging.error("没有默认用户！请添加或者设置一个默认用户。")
        exit(-6)

    if args.action == 'add':
        add_user(target_user)
        logging.info("添加成功")
        exit(0)

    # 检测用户列表是否为空，如果为空，则敦促用户添加并设置默认用户。
    if len(config['users']) == 0:
        logging.error("请添加并设置默认用户 ipgw add -u 20180001 && ipgw default -u 20180001")
        exit(-5)

    # 接下来，需要处理网络登录登出问题了。
    main_ipgw = IPGW()
    if target_sid:  # 如果用户指定了sid，那么用户一定是想下线这个设备。我们不如先尝试下线一下用户的这个设备，如果成功就ok了。
        try:
            main_ipgw.logout(target_sid)
        except RequestNeedCASAuthenticError:  # 用户需要认证
            pass
        else:
            # 如果用户直接下线成功……
            logging.info("快速下线成功！")
            exit(0)  # 直接退出程序。
    while True:
        current_login_result = main_ipgw.login(target_user['username'], target_user['password'])
        if current_login_result == LoginResult.UsernameOrPasswordError:
            logging.error(f"用户名或密码错误，剩余尝试次数{main_ipgw.last_trial_times}")
            exit(5)
        elif current_login_result == LoginResult.AttemptReachLimit:
            logging.error("尝试次数达到上限")
            exit(15)
        elif current_login_result == LoginResult.LoginSuccessful:
            logging.info("登录成功")
            # 打印登录状态
            current_ipgw_status = main_ipgw.get_ipgw_status()

            if current_ipgw_status == PageStatus.Normal:
                print_ipgw_status(main_ipgw.success_page)
                break

            elif current_ipgw_status == PageStatus.OtherDeviceOnline:
                # 有其他设备在线！看看kick方法是怎么定义的行为？
                logging.info(f"其他设备在线，执行操作{kick_action}")
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
                logging.error('用户已经暂停服务')
                exit(-2)
            elif current_ipgw_status == PageStatus.InsufficientFee:
                logging.error('此账号余额不足月租，无法继续使用')
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
            logging.info("自我下线")
        elif args.only:
            logging.info("仅保留自己在线")
        elif logout_all_devices:
            logging.info("已经全部下线")
        exit(0)

#
# if __name__ == '__main__':
#     main()
