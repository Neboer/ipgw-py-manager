#!/usr/bin/env python3
import argparse, getpass
from sessionreq import connect_to_ipgw_by_unpw
from parse_login_result import parse_login_result, get_devices_data, other_account, base_info, drop_device

parser = argparse.ArgumentParser(description="NEU ipgw manage client")
parser.add_argument('-v', '--version', action='version', version='NEU ipgw manage client V1.0 by Neboer')
parser.add_argument('-i', action='store_true', help='login with stored NEU-pass username and password',
                    dest='login')
parser.add_argument('--login', default=None, help='login with specified username.', dest='username')
parser.add_argument('-o', action='store_true', help='log out all devices connected to the network', dest='logout_all')
parser.add_argument('--self', action='store_true', help='if set, logout or query your current device only.')
parser.add_argument('--other', action='store_true', help='if set, just logout or query your other devices.')
parser.add_argument('--logout', default=None, help='logout specified id', dest='uid')
parser.add_argument('-q', '--quiet', action='store_true', default=None, help='quiet mode, no output')
parser.add_argument('-c', '--current', default=None, help='list devices and show the detail info of every device')
parser.add_argument('-s', '--status', action='store_true', default=None,
                    help='show the detail of your ipgw account, needs web center\'s password. ')
parser.add_argument('--config', action='store_true', help='open configure file with a text editor.')
args = parser.parse_args()


def normal_login(username, password):
    result = connect_to_ipgw_by_unpw(username, password)
    if type(result) is int:
        print("username or password error, last try time " + str(result))
    else:
        login_data_soup = parse_login_result(result)
        ifOtherAccountLoginUid = other_account(result)
        if ifOtherAccountLoginUid:
            print("other account login, uid:" + ifOtherAccountLoginUid)
        basicInformation = base_info(login_data_soup)
        print("account: {}\nip: {}\nconsumed: {}\nonline: {}\n".format(basicInformation[0], basicInformation[1],
                                                                       basicInformation[2], basicInformation[3]))
        for device in get_devices_data(login_data_soup):
            print(device)


if args.login:
    normal_login("username", "password")

if args.uid:
    drop_device(args.uid)
    print("drop request sent")

if args.username:
    password = getpass.getpass()
    normal_login(args.username, password)
