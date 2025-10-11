#!/usr/bin/env python
# coding:utf-8
"""将个人封装的公共方法打包"""
from setuptools import setup, find_packages
from deng import __version__


PACKAGE_NAME = "deng"
PACKAGE_VERSION = __version__

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="Personal method encapsulation",
    url="https://github.com/Deng2016/deng",
    author="dengqingyong",
    author_email="yu12377@163.com",
    packages=find_packages(),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    exclude_package_data={"": [".gitignore", "lab.py"]},
    install_requires=[
        "requests>=2.26.0",
        "redis>=4.5.0",
        "pycryptodome>=3.15.0",
        "xpinyin>=0.7.6",
        "pysmb>=1.2.10",
        "pyjwt>=2.8.0",
        "pytz>=2025.2",
        "pymysql>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
    ],
)
