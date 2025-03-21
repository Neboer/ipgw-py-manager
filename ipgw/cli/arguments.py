import argparse
from pathlib import Path
import os

import ipgw
from ipgw.core.config import get_config_path

parser = argparse.ArgumentParser(description='ipgw-py-manager', epilog=f'配置文件路径：{get_config_path()}')
parser.add_argument('action', type=str, default='login',
                    choices=['login', 'logout', 'add', 'i', 'o', 'default', 'status', 's'])
parser.add_argument('--username', '-u', type=str, help='学工号，用户名')
parser.add_argument('--password', '-p', type=str, help='在命令行中指定的密码，不推荐使用')
parser.add_argument('--all', '-a', action='store_true', help='下线所有设备')
parser.add_argument('--version', '-V', action='version', version=f'NEU-ipgw-manager version {ipgw.__version__}', help='显示软件版本信息')
parser.add_argument('--verbose', '-v', action='store_true', help='详细输出日志')
parser.add_argument('--use-proxy', action='store_true', help='启用系统代理设置（默认禁用所有代理）')
parser.add_argument('--http-proxy', type=str, help='指定HTTP代理服务器地址')
parser.add_argument('--https-proxy', type=str, help='指定HTTPS代理服务器地址')

args = parser.parse_args()
if args.action == 'i':
    args.action = 'login'
if args.action == 'o':
    args.action = 'logout'
if args.action == 's':
    args.action = 'status'

# Set environment variables based on command-line arguments for proxy settings
if not args.use_proxy:
    # Disable all proxies by default unless --use-proxy is specified
    os.environ['NO_PROXY'] = '*'
if args.http_proxy:
    os.environ['HTTP_PROXY'] = args.http_proxy
if args.https_proxy:
    os.environ['HTTPS_PROXY'] = args.https_proxy
