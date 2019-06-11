#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(description="NEU ipgw manage client")
parser.add_argument('-i', '--login', nargs='?', action="store_true", default=True)  # login option, can be ignored
parser.add_argument('-o', '--logout', nargs=1, action="store_true")
