import os, shutil


def install():
    homepath = os.getenv("HOME")
    os.mkdir(os.path.join(homepath, ".ipgw-py-manager"))
    shutil.copy("settings.json", os.path.join(homepath, ".ipgw-py-manager"))
    print("you can run ")
