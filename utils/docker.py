#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: docker
# @date: 2023/9/14
import io
import os
import subprocess
import tarfile

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


def check_image_has_built(image_name: str):
    """
    check_image_has_built 检查镜像是否已经构建
    :param image_name:
    :return:
    """
    client = docker.from_env()
    try:
        client.images.get(image_name)
        return True
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
    if container:
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


def push_files(container, src: str, target: str):
    """
    push_files
    :param container:
    :param src:
    :param target:
    :return:
    """
    if container and container.status == 'running':
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w|') as tar, open(src, 'rb') as f:
            info = tar.gettarinfo(fileobj=f)
            info.name = os.path.basename(src)
            tar.addfile(info, f)
        container.put_archive(target, stream.getvalue())


def start_container(image_name: str, container_name: str, force_remove: bool = False, reload: bool = True, **kwargs):
    """
    拉取镜像
    :return:
    """
    client = docker.from_env()
    _, container = check_is_alive(container_name)
    if container and container.status == 'running':
        if force_remove:
            container.stop()
            container.remove()
        if reload:
            container.restart()
            return

    container = client.containers.run(
        image=image_name,
        name=container_name,
        detach=True,
        **kwargs
    )
    return container


def build_redis_container():
    """
    build_mysql_container
    :return:
    """
    container_name = 'redis'
    image_name = 'redis'

    _, container = check_is_alive(container_name)
    if not container:
        start_container(image_name, container_name)
    if container.status != 'running':
        container.start()
    return container


def build_image(work_dir: str, tag: str):
    """
    build image
    :param tag:
    :param work_dir:
    :return:
    """
    client = docker.from_env()
    client.images.build(path=work_dir, tag=tag)
    return True
