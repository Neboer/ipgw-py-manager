from .arguments import args
from ..core.errors_modals import *
from ..core.config import config, add_user, set_default_username, update_last_login_info
from .get_info import get_settings
from .print_status import print_ipgw_status
import logging
# ipgw的命令行界面。
from ..core.ipgw import IPGW

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
            else:
                # 接下来，需要处理网络登录登出问题了。
                main_ipgw = IPGW()
                current_ipgw_status = main_ipgw.get_status()
                if args.action == 'status':
                    print_ipgw_status(current_ipgw_status)
                elif args.action == 'logout':
                    if current_ipgw_status['error'] == 'not_online_error':  # 当前ip没有在线
                        logging.error("ip不在线，无法下线")
                    elif current_ipgw_status['error'] == 'ok':  # 当前ip已经在线
                        if args.all:
                            main_ipgw.batch_logout()
                            logging.info("成功断开所有连接")
                        else:
                            main_ipgw.advanced_logout(current_ipgw_status['user_name'],
                                                      current_ipgw_status['online_ip'])
                            logging.info("成功注销当前账号")
                elif args.action == 'login':
                    if current_ipgw_status['error'] == 'ok':
                        logging.error("ip已经在线，无需登录")
                    elif current_ipgw_status['error'] == 'not_online_error':
                        # ip不在线，需要登录
                        current_login_result = main_ipgw.login(target_user['username'], target_user['password'])
                        if current_login_result == LoginResult.UsernameOrPasswordError:
                            logging.error("用户名或密码错误")
                        elif current_login_result == LoginResult.LoginSuccessful:
                            logging.info("登录成功")
                            current_ipgw_status = main_ipgw.get_status(must_success=True)
                            # 打印登录状态
                            print_ipgw_status(current_ipgw_status)
                            # 将用户信息写入配置文件。
                            update_last_login_info(current_ipgw_status['user_name'], current_ipgw_status['online_ip'])
                        elif current_login_result == LoginResult.ArrearageUserError:
                            logging.error("用户已欠费")
                        elif current_login_result == LoginResult.UserAlreadyOnlineError:
                            logging.error("用户已经在线了")


if __name__ == '__main__':
    main()
