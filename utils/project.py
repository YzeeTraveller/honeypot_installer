#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: project
# @date: 2023/9/14


import os

import configparser


def get_project_root():
    """
    get_project_root
    :return:
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_ini_file(src: str) -> configparser.ConfigParser:
    """
    read_ini_file
    :param src:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(src)
    return config
