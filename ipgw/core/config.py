import json
from os import getenv
from pathlib import Path
from typing import TypedDict, List, Any, Union
from .errors_modals import *


class User(TypedDict, total=False):
    username: str
    password: str
    is_default: bool

    last_login_time: str
    consumed_bytes: int

    last_login_result: str


class Config(TypedDict):
    users: List[User]
    ua: str
    default_kick: str  # 默认当“已经有人在此ip了”的行为，默认是“relogin”

    last_login_username: str  # 上次登录的用户名
    last_sid: str  # 上次登录的设备编号。


base_dir = Path.home() if not getenv('IPGW_CONFIG_FILE') else Path(getenv('IPGW_CONFIG_FILE'))
config_file_location = base_dir.joinpath('ipgw.json')

with open(config_file_location, 'r', encoding='utf8') as config_file:
    config: Config = json.load(config_file)


def update_config_file():
    global config
    with open(config_file_location, 'w', encoding='utf8') as writable_config_file:
        json.dump(config, writable_config_file, ensure_ascii=False, indent=4)


def add_user(user_dict: User) -> None:
    if "is_default" not in user_dict.keys():
        user_dict['is_default'] = False
    config["users"].append(user_dict)
    update_config_file()


def query_user_by_username(username: str) -> Union[User, None]:
    users_list = config["users"]
    return next((x for x in users_list if x['username'] == username), None)


def query_default_user() -> User:
    users_list = config["users"]
    result = next((x for x in users_list if x['is_default']), None)
    if not result:
        raise NoDefaultUserError
    return result


def set_default_username(username: str) -> None:
    find = False
    for user in config["users"]:
        if user["username"] == username:
            user["is_default"] = True
            find = True
        else:
            user["is_default"] = False
    if not find:
        raise UsernameNotInConfigFileError
    update_config_file()


def update_last_login_info(username="", sid=""):
    if username:
        config['last_login_username'] = username
    if sid:
        config['last_sid'] = sid
    update_config_file()


def query_last_user() -> User:
    return query_user_by_username(config['last_login_username'])
