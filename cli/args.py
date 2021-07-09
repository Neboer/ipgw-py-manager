import argparse

parser = argparse.ArgumentParser(description='ipgw-py-manager')
parser.add_argument('action', type=str, default='login', choices=['login', 'logout', 'add', 'i', 'o', 'default'])
parser.add_argument('--username', '-u', type=str)
parser.add_argument('--password', '-p', type=str)
parser.add_argument('--sid', '-s', type=str)
parser.add_argument('--only', action='store_true')
parser.add_argument('--self', action='store_true')
parser.add_argument('--silent', action='store_true')
parser.add_argument('--kick', '-k', default=None, choices=['relogin', 'exit', 'logout'])
parser.add_argument('--last', '-l', action='store_true')

args = parser.parse_args()
if args.action == 'i':
    args.action = 'login'
if args.action == 'o':
    args.action = 'logout'
