import argparse


def parse_argument():
    parser = argparse.ArgumentParser(description="NEU ipgw managing client")
    parser.add_argument('-v', '--version', action='version',
                        version='NEU ipgw manage client V4.0 formal edition by Neboer!')
    parser.add_argument('-i', '--login', action='store_true', help='login with stored NEU-pass username and password',
                        dest='login')
    parser.add_argument('-u', '--username', default=None, help='set a username to login/logout', dest='username')
    parser.add_argument('-o', action='store_true', help='log out all devices connected to the network.',
                        dest='logout_all')
    parser.add_argument('--nocookie', action='store_true', help='request without cookies and neither store them')
    parser.add_argument('--recookie', action='store_true', help='request without cookies but store them')
    # parser.add_argument('--self', action='store_true', help='if set, logout or query your current device only.')
    # parser.add_argument('--other', action='store_true', help='if set, just logout or query your other devices.')
    parser.add_argument('--logout', default=None, help='logout specified id', dest='uid')
    parser.add_argument('--other', action='store_true', help='logout other account which logged on current ip.')
    # parser.add_argument('-c', '--current', action="store_true", help='list devices and show the detail info of each device')
    # parser.add_argument('-s', '--status', action='store_true', default=None,
    #                     help='show the detail of your ipgw account, needs web center\'s password. ')
    parser.add_argument('--config', default=None, help='open configure file with specific text editor.')
    return parser.parse_args()
