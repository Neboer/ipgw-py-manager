#!/usr/bin/env python3
import argparse, getpass, os, requests, json
from login import login, read_settings_into_session, print_fail_auth, print_login_successful, read_unpw_from_settings
from requestresult import UnionAuth, SuccessPage, Device

parser = argparse.ArgumentParser(description="NEU ipgw managing client")
parser.add_argument('-v', '--version', action='version',
                    version='NEU ipgw manage client V1.0 by Neboer\nuse ipgw -h show more info')
parser.add_argument('-i', '--login', action='store_true', help='login with stored NEU-pass username and password',
                    dest='login')
parser.add_argument('-u', '--username', default=None, help='set a username to login/logout', dest='username')
parser.add_argument('-o', action='store_true', help='log out all devices connected to the network', dest='logout_all')
parser.add_argument('--nocookie', action='store_true', help='request without cookies and neither store them')
parser.add_argument('--recookie', action='store_true', help='request without cookies but store them')
# parser.add_argument('--self', action='store_true', help='if set, logout or query your current device only.')
# parser.add_argument('--other', action='store_true', help='if set, just logout or query your other devices.')
parser.add_argument('--logout', default=None, help='logout specified id', dest='uid')
# parser.add_argument('-c', '--current', action="store_true", help='list devices and show the detail info of each device')
# parser.add_argument('-s', '--status', action='store_true', default=None,
#                     help='show the detail of your ipgw account, needs web center\'s password. ')
parser.add_argument('--config', default=None, help='open configure file with specific text editor.')
args = parser.parse_args()

setting_file_location = os.getenv("HOME") + "/.ipgw-py-manager/settings.json"
with open(setting_file_location, "r") as file:
    settings = json.load(file)
flags_sum = args.login + args.logout_all + (args.uid is not None)
if flags_sum == 0:
    if args.config:
        os.system(args.config + " " + setting_file_location)
        exit(0)

if flags_sum > 1:
    print("error, multi-action is not allowed")

global_session = requests.session()
if args.nocookie or args.recookie:
    read_settings_into_session(settings, global_session, False)
else:
    read_settings_into_session(settings, global_session, True)

if args.login:
    if args.username:  # 如果用户指定了用户名，则用指定的用户名登录
        password = getpass.getpass()
        login_result = login(global_session, args.username, password)
        if type(login_result) is UnionAuth:
            print_fail_auth(login_result)
        elif type(login_result) is SuccessPage:
            print_login_successful(login_result)
        else:
            print("unknown request result.")
    else:
        result = login(global_session)
        if type(result) is UnionAuth:  # cookie错误或没有cookie。
            print("cookie empty or error. login with stored username.")
            unpw = read_unpw_from_settings(settings)
            result = result.login(unpw[0], unpw[1], global_session)
            if type(result) is UnionAuth:
                print_fail_auth(result)
            elif result is None:
                print("unknown request result")
        elif result is None:
            print("unknown request result")
        print_login_successful(result)

if args.uid:
    if Device.logout_sid(args.uid, global_session):
        print("logout {} successful".format(args.uid))
    else:
        print("logout {} error".format(args.uid))

if args.logout_all:
    if args.username:  # 如果用户指定了用户名，则用指定的用户名登录
        password = getpass.getpass()
        login_result = login(global_session, args.username, password)
        if type(login_result) is UnionAuth:
            print_fail_auth(login_result)
        elif type(login_result) is SuccessPage:
            for device in login_result.device_list:  # type: Device
                if device.logout(global_session):
                    print("logout {} successful".format(device.sid))
                else:
                    print("logout {} error".format(device.sid))
        else:
            print("unknown request result.")
    else:
        result = login(global_session)
        if type(result) is UnionAuth:  # cookie错误或没有cookie。
            print("cookie error. login with stored username.")
            unpw = read_unpw_from_settings(settings)
            result = result.login(unpw[0], unpw[1], global_session)
            if type(result) is UnionAuth:
                print_fail_auth(result)
            elif result is None:
                print("unknown request result")
        elif result is None:
            print("unknown request result")
        else:
            for device in result.device_list:  # type: Device
                if device.logout(global_session):
                    print("logout {} successful".format(device.sid))
                else:
                    print("logout {} error".format(device.sid))

if not args.nocookie:
    new_cookies = requests.utils.dict_from_cookiejar(global_session.cookies)
    settings["ipgw_cookie_jar"] = new_cookies
    with open(setting_file_location, "w") as setting_file:
        json.dump(settings, setting_file, indent=4)
