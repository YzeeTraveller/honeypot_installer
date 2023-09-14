#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: docker
# @date: 2023/9/14

import subprocess

import docker


def is_docker_installed():
    """
    is_docker_installed 是否安装docker
    :return:
    """
    try:
        subprocess.check_output(["docker", "--version"])
        return True
    except subprocess.CalledProcessError:
        return False
    except:
        return False


def check_is_alive(container_name: str):
    """
    check_is_alive 判断是否存活
    :return:
    """
    client = docker.from_env()
    try:
        c = client.containers.get(container_name)
        return True, c
    except:
        return False, None


def stop_and_remove_container(container):
    """
    stop_and_remove_container 停止和运行容器
    :param container:
    :return:
    """
    if container and container.status == 'running':
        container.stop()
        container.remove()


def export_files(container, src: str, target: str):
    """
    export_files 导出文件
    :param container:
    :param dir_path:
    :return:
    """
    if container and container.status == 'running':
        with open(target, "wb") as host_file:
            bits, stat = container.get_archive(src)
            for chunk in bits:
                host_file.write(chunk)
