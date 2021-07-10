#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        from shutil import copy
        from pathlib import Path

        current_position = Path(__file__).parent.joinpath('default_config.json')
        target_destination = Path.home().joinpath('ipgw.json')
        copy(current_position, target_destination)


setup(
    name="NEU-ipgw-manager",
    version="2.0",
    author="Neboer",
    author_email="rubinposter@gmail.com",
    url="https://github.com/Neboer/ipgw-py-manager",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    description="ipgw manager for NEU network gateway",
    long_description=open("README.md", encoding='utf8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        "console_scripts": "ipgw = ipgw.cli.ipgw:main"
    },
    cmdclass={'install': PostInstallCommand},
    # package_data={"": ["default_config.json"]},
    include_package_data=True,
    install_requires=['tabulate', 'requests', 'beautifulsoup4', 'wcwidth', 'lxml'],
)
