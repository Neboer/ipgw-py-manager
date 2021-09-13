import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='ipgw-py-manager', epilog=f'配置文件路径：{Path.home().joinpath("ipgw.json")}')
parser.add_argument('action', type=str, default='login', choices=['login', 'logout', 'add', 'i', 'o', 'default'])
parser.add_argument('--username', '-u', type=str, help='学工号，用户名')
parser.add_argument('--password', '-p', type=str, help='在命令行中指定的密码，不推荐使用')
parser.add_argument('--sid', '-s', type=str, help='指定需要下线的设备')
parser.add_argument('--only', action='store_true', help='只保留自己在线')
parser.add_argument('--self', action='store_true', help='登录帐号之后，只下线自己，登录了个寂寞')
parser.add_argument('--silent', action='store_true', help='不打印登录成功之后的帐号信息')
parser.add_argument('--kick', '-k', default=None, choices=['relogin', 'exit', 'logout'], help='当已经有用户在线时采取的操作')
parser.add_argument('--last', '-l', action='store_true', help='使用最后一次登录的信息操作ipgw网关')
parser.add_argument('--version', '-v', action='version', version='NEU-ipgw-manager version 2.0.2 preview')

args = parser.parse_args()
if args.action == 'i':
    args.action = 'login'
if args.action == 'o':
    args.action = 'logout'
