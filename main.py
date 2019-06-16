#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(description="NEU ipgw manage client")
parser.add_argument('-v', '--version', action='version', version='NEU ipgw manage client V1.0 by Neboer')
parser.add_argument('-i', action='store_true', help='login with stored NEU-pass username and password',
                    dest='one_login')
parser.add_argument('--login', default=None, help='login with specified username.', dest='login_username')
parser.add_argument('-o', action='store_true', help='log out all devices connected to the network', dest='logout_all')
parser.add_argument('--self', action='store_true', help='if set, logout or query your current device only.')
parser.add_argument('--other', action='store_true', help='if set, just logout or query your other devices.')
parser.add_argument('--logout', default=None, help='logout specified id', dest='logout_uid')
parser.add_argument('-q', '--quiet', action='store_true', default=None, help='quiet mode, no output')
parser.add_argument('-c', '--current', default=None, help='list devices and show the detail info of every device')
parser.add_argument('-s', '--status', action='store_true', default=None,
                    help='show the detail of your ipgw account, needs web center\'s password. ')

args = parser.parse_args()
print(args)
