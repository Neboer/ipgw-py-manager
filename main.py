#!/usr/bin/env python3
import argparse, getpass, json, os, re
from sessionreq import connect_to_ipgw_by_unpw
from parse_login_result import parse_login_result, get_devices_data, other_account, base_info, drop_device

parser = argparse.ArgumentParser(description="NEU ipgw managing client")
parser.add_argument('-v', '--version', action='version', version='NEU ipgw manage client V1.0 by Neboer')
parser.add_argument('-i', '--login', action='store_true', help='login with stored NEU-pass username and password',
                    dest='login')
parser.add_argument('-u', '--username', default=None, help='set a username to login/logout', dest='username')
parser.add_argument('-o', action='store_true', help='log out all devices connected to the network', dest='logout_all')
# parser.add_argument('--self', action='store_true', help='if set, logout or query your current device only.')
# parser.add_argument('--other', action='store_true', help='if set, just logout or query your other devices.')
parser.add_argument('--logout', default=None, help='logout specified id', dest='uid')
parser.add_argument('-q', '--quiet', action='store_true', default=None, help='quiet mode, no output')
parser.add_argument('-c', '--current', action="store_true", help='list devices and show the detail info of each device')
# parser.add_argument('-s', '--status', action='store_true', default=None,
#                     help='show the detail of your ipgw account, needs web center\'s password. ')
parser.add_argument('--config', default=None, help='open configure file with specific text editor.')
parser.add_argument('--change_location', default=None, help='change config file location which stored in the code',
                    dest='config_file_location')
args = parser.parse_args()

homepath = os.getenv("HOME")
setting_file_location = homepath + "/.ipgw-py-manager/settings.json"
with open(setting_file_location, "r") as setting_file:
    settings = json.load(setting_file)


def normal_login(username, password):
    if username == "" or password == "":
        print("username or password is empty, exit.")
        exit(1)
    result = connect_to_ipgw_by_unpw(username, password, settings)
    with open(setting_file_location, "w") as setting_file:
        json.dump(settings, setting_file, indent=4)
    if type(result) is int:
        if result == -1:
            print("fail 5 times, ip will be locked for 1 min")
            return
        print("username or password error, last try time " + str(result))
        return
    else:
        login_data_soup = parse_login_result(result)
        ifOtherAccountLoginUid = other_account(result)
        if ifOtherAccountLoginUid:
            print("other account login, uid:" + ifOtherAccountLoginUid)
        else:
            return base_info(login_data_soup), get_devices_data(login_data_soup)
        #     basicInformation =
        #     print("account: {}\nip: {}\nconsumed: {}\nonline: {}\n".format(basicInformation[0], basicInformation[1],
        #                                                                    basicInformation[2], basicInformation[3]))
        # for device in
        #     print(device)


def print_login_result(info_and_basic_data_tuple: (tuple, list)):
    if not info_and_basic_data_tuple:
        return
    basic_information = info_and_basic_data_tuple[0]
    print("account: {}\nip: {}\nconsumed: {}\nonline: {}\n".format(basic_information[0], basic_information[1],
                                                                   basic_information[2], basic_information[3]))
    for device in info_and_basic_data_tuple[1]:
        print(device)


if args.login:
    if args.username:  # 如果用户指定了用户名，则用指定的用户名登录
        password = getpass.getpass()
        print_login_result(normal_login(args.username, password))
    else:
        print_login_result(normal_login(settings["unity_login"]["username"],
                                        settings["unity_login"]["password"]))  # use default settings

if args.uid:
    drop_device(args.uid)
    print("drop request sent")

if args.logout_all:
    if args.username:
        password = getpass.getpass()
        device_info_list = normal_login(args.username, password)[1]
        for device in device_info_list:
            device.logout()
            print("drop request sent ", device.uid)
    else:
        device_info_list = normal_login(settings["unity_login"]["username"], settings["unity_login"]["password"])[1]
        for device in device_info_list:
            device.logout()
            print("drop request sent ", device.uid)

if args.config:
    os.system(args.config + " " + setting_file_location)
    exit(0)

if args.config_file_location:
    abspath = os.path.realpath(__file__)
    print("rewrite default config path in ", abspath)
    thisfile = open(abspath, 'r+')
    newfiledata = re.sub(r"setting_file_location = \"(.*)\"",
                         "setting_file_location = \"" + args.config_file_location + "\"", thisfile.read())
    print(newfiledata)
    thisfile.close()
    exit(0)
