from shutil import copy
from pathlib import Path

default_config_file_location = Path(__file__).parent.joinpath('default_config.json')
target_destination = Path.home().joinpath('ipgw.json')
copy(default_config_file_location, target_destination)
