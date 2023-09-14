#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: project
# @date: 2023/9/14


import os


def get_project_root():
    """
    get_project_root
    :return:
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
