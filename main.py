#!/usr/bin/env python3
import os, requests, json
from show_result import read_settings_into_session
from login_process import whole_process
from argument import parse_argument
from requestresult import Device

args = parse_argument()

setting_file_location = os.path.join(os.getenv("HOME"), ".ipgw-py-manager", "settings.json")
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
global_session.max_redirects = 2
cookie_is_set = False
if args.nocookie or args.recookie or (args.username is not None):
    read_settings_into_session(settings, global_session, False)
else:
    read_settings_into_session(settings, global_session, True)
    cookie_is_set = True

if args.login:
    whole_process(args.username, global_session, settings, True)

if args.uid:
    if Device.logout_sid(args.uid, global_session):
        print("logout {} successful".format(args.uid))
    else:
        print("logout {} error".format(args.uid))

if args.logout_all:
    whole_process(args.username, global_session, settings, False)

if not args.nocookie:
    new_cookies = requests.utils.dict_from_cookiejar(global_session.cookies)
    settings["ipgw_cookie_jar"] = new_cookies
    with open(setting_file_location, "w") as setting_file:
        json.dump(settings, setting_file, indent=4)
