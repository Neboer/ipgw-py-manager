import json
import logging
from pathlib import Path
from typing import List, Union
from platformdirs import user_config_dir

from .errors_modals import *


class User(TypedDict, total=False):
    username: str
    password: str
    is_default: bool

    last_login_time: str
    consumed_bytes: int

    last_login_result: str


default_config_dict = {
    "users": [],
    "ua": "",
    "default_kick": "relogin",
    "last_login_username": "",
    "last_sid": ""
}


class Config(TypedDict):
    users: List[User]
    last_login_username: str  # 上次登录的用户名
    last_ip_addr: str


def get_config_path() -> Path:
    return Path(user_config_dir('ipgw', roaming=True)) / 'ipgw.json'


config_file_location = get_config_path()
if not config_file_location.exists():
    # 配置文件不存在，且无冲突，我们创建一个配置文件。
    logging.warning(f"配置文件不存在，自动创建在{config_file_location}。")
    config_file_location.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file_location, 'w', encoding='utf8') as config_file:
        json.dump(default_config_dict, config_file)
    logging.info(f"请使用 ipgw add -u xxx 和 ipgw default -u xxx 两个命令来添加新账号并将其设为默认。")

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


def update_last_login_info(username="", ip_addr=""):
    if username:
        config['last_login_username'] = username
    if ip_addr:
        config['last_ip_addr'] = ip_addr
    update_config_file()


def query_last_user() -> User:
    return query_user_by_username(config['last_login_username'])
