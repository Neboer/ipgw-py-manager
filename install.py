#!/usr/bin/env python3
import os, shutil


def install():
    homepath = os.getenv("HOME")
    os.mkdir(os.path.join(homepath, ".ipgw-py-manager"))
    shutil.copy("settings.json", os.path.join(homepath, ".ipgw-py-manager"))
    print("now you should run ./main.py --config vim or use other text editor, change your default username and password in configuration file.")

install()