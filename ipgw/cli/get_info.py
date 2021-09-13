# 从配置文件和命令行参数中猜测需要使用的用户以及可能被覆盖的设置(比如kick)。
from ..core.config import User, config, query_default_user, query_user_by_username, query_last_user
from .arguments import args
from getpass import getpass
from typing import Tuple


def get_settings():  # type: ()->Tuple[User, str, str] # 分别是：目标用户、sid、kick三个值。
    target_user: User = {}
    target_sid: str = args.sid if args.sid else None  # 如果用户指定了sid，那么这就是目标。如果用户没有指定，但是指定了last，那配置文件里记载的sid就是目标。
    kick_action = args.kick if args.kick else config["default_kick"]

    if args.last:
        # 如果程序指定了last选项，那么假装用户输入了对应的最后信息。
        target_user = query_last_user()
        target_sid = config['last_sid']
    else:
        if not args.username:
            # 如果没有指定用户名，则使用默认用户身份。
            target_user = query_default_user()
        else:
            # 程序指定了用户名，先查询是否有此用户的密码。
            target_user["username"] = args.username
            if args.password:
                target_user["password"] = args.password
            else:
                # 如果用户没有提供用户名，先看看配置文件里有没有保存用户。
                t = query_user_by_username(args.username)
                if t:  # 如果找到了
                    target_user = t
                else:  # 如果没找到，请用户输入。
                    target_user["password"] = getpass('输入密码：')
    return target_user, target_sid, kick_action
    # 经过这番折腾，应该有用户名和密码了。
