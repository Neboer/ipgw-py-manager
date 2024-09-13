import argparse
from pathlib import Path

import ipgw

parser = argparse.ArgumentParser(description='ipgw-py-manager', epilog=f'配置文件路径：{Path.home().joinpath("ipgw.json")}')
parser.add_argument('action', type=str, default='login',
                    choices=['login', 'logout', 'add', 'i', 'o', 'default', 'status', 's'])
parser.add_argument('--username', '-u', type=str, help='学工号，用户名')
parser.add_argument('--password', '-p', type=str, help='在命令行中指定的密码，不推荐使用')
parser.add_argument('--all', '-a', action='store_true', help='下线所有设备')
parser.add_argument('--version', '-V', action='version', version=f'NEU-ipgw-manager version {ipgw.__version__}')
parser.add_argument('--verbose', '-v', action='store_true')

args = parser.parse_args()
if args.action == 'i':
    args.action = 'login'
if args.action == 'o':
    args.action = 'logout'
if args.action == 's':
    args.action = 'status'
