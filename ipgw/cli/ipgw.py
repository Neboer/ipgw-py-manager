from typing import cast

from ipgw.core.api.portal import IPGWNotOnlineInfo, IPGWOnlineInfo

from .arguments import args
from ..core.errors_modals import *
from ..core.config import config, add_user, set_default_username, update_last_login_info, save_mobile_tgt, load_mobile_tgt
from .get_info import get_settings
from .print_status import print_ipgw_status
import logging
# ipgw的命令行界面。
from ..core.ipgw import IPGW
from ..core.api.sso_mobile_error import MobileSSOLoginFailedError

logging.basicConfig(format='%(message)s', level=logging.INFO if not args.verbose else logging.DEBUG)


def main():
    # 程序第0步：如果需要设置默认登录用户，那么就设置。
    if args.action == 'default':
        set_default_username(args.username)
        logging.info('设置成功。')
    else:
        # 查明用户
        try:
            target_user = get_settings()
        except NoDefaultUserError:
            # 检测用户列表是否为空，如果为空，则敦促用户添加并设置默认用户。
            if len(config['users']) == 0:
                logging.error("请添加并设置默认用户 ipgw add -u 20180001 && ipgw default -u 20180001")
                return -5
            else:
                logging.error("没有默认用户！请添加或者设置一个默认用户。")
                return -6
        else:
            if args.action == 'add':
                add_user(target_user)
                logging.info("添加成功")
            elif args.action == 'mobile-login':
                username = target_user.get('username')
                password = target_user.get('password')
                if not username or not password:
                    logging.error("缺少用户名或密码，无法获取 TGT")
                    return -7

                main_ipgw = IPGW(bypass_proxy=args.bypass_system_proxy, mobile=True)

                def _get_sms_code() -> str:
                    return input("请输入短信验证码: ")

                try:
                    tgt = main_ipgw.acquire_mobile_tgt(username, password, _get_sms_code)
                except MobileSSOLoginFailedError:
                    logging.error("用户名或密码错误")
                    return -8

                save_mobile_tgt(username, tgt)
                logging.info("TGT 获取成功，已保存")
            else:
                # 接下来，需要处理网络登录登出问题了。
                main_ipgw = IPGW(bypass_proxy=args.bypass_system_proxy, mobile=args.mobile)
                current_status = main_ipgw.get_status()
                if args.action == 'status':
                    print_ipgw_status(current_status)
                elif args.action == 'logout':
                    if current_status['error'] == 'not_online_error':  # 当前ip没有在线
                        logging.error("ip不在线，无法下线")
                    elif current_status['error'] == 'ok':  # 当前ip已经在线
                        current_status = cast(IPGWOnlineInfo, current_status)
                        if args.all:
                            main_ipgw.batch_logout()
                            logging.info("成功断开所有连接")
                        else:
                            main_ipgw.advanced_logout(current_status['user_name'],
                                                      current_status['online_ip'])
                            logging.info("成功注销当前账号")
                elif args.action == 'login':
                    if current_status['error'] == 'ok':
                        logging.error("ip已经在线，无需登录")
                    elif current_status['error'] == 'not_online_error':
                        # ip不在线，需要登录
                        username = target_user.get('username')
                        password = target_user.get('password')
                        if not username or not password:
                            logging.error("缺少用户名或密码，无法登录")
                            return -7
                        if args.mobile:
                            tgt = load_mobile_tgt(username)
                            if tgt is None:
                                logging.error("未找到 TGT，请先运行 ipgw mobile-login 获取 TGT")
                                return -8
                            current_login_result = main_ipgw.login_with_mobile_tgt(tgt)
                            if current_login_result == LoginResult.UsernameOrPasswordError:
                                logging.error("TGT 已过期，请重新运行 ipgw mobile-login 获取 TGT")
                                return -8
                        else:
                            current_login_result = main_ipgw.login(username, password)
                            if current_login_result == LoginResult.UsernameOrPasswordError:
                                logging.error("用户名或密码错误")
                        if current_login_result == LoginResult.LoginSuccessful:
                            logging.info("登录成功")
                            current_status = main_ipgw.get_status(must_success=True)
                            current_status = cast(IPGWOnlineInfo, current_status)
                            # 打印登录状态
                            print_ipgw_status(current_status)
                            # 将用户信息写入配置文件。
                            update_last_login_info(current_status['user_name'], current_status['online_ip'])
                        elif current_login_result == LoginResult.ArrearageUserError:
                            logging.error("用户已欠费")
                        elif current_login_result == LoginResult.UserAlreadyOnlineError:
                            logging.error("用户已经在线了")


if __name__ == '__main__':
    main()
