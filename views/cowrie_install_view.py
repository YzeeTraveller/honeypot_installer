#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: cowrie
# @date: 2023/9/14

import time

import flet as ft

import docker

from utils.docker import (
    check_is_alive,
    stop_and_remove_container,
)
from utils.views import (
    force_refresh_view,
    generate_container_alive_status,
    generate_container_op_buttons,
)


_ROUTE = '/install/cowrie'
_IMAGE_NAME = 'cowrie/cowrie:latest'
_CONTAINER_NAME = 'cowire'


def start_event(event: ft.ControlEvent):
    """
    安装运行
    :return:
    """
    page = event.page

    this: ft.ElevatedButton = event.control
    this.disabled = True
    page.update()

    client = docker.from_env()
    container_name = _CONTAINER_NAME
    image_name = _IMAGE_NAME
    port_bindings = {2222: 2222}
    constainer = client.containers.run(
        image=image_name,
        name=container_name,
        detach=True,
        ports=port_bindings,
    )

    this.disabled = False
    page.update()
    time.sleep(1)
    force_refresh_view(page, _ROUTE)

    return constainer.id


def stop_event(event):
    """
    停止
    :return:
    """
    page = event.page

    this: ft.ElevatedButton = event.control
    this.disabled = True
    page.update()

    exists, container = check_is_alive(_CONTAINER_NAME)
    if container:
        stop_and_remove_container(container)

    time.sleep(1)
    this.disabled = False
    page.update()
    time.sleep(1)
    force_refresh_view(page, _ROUTE)


def configure(event):
    """
    选择配置
    :return:
    """
    page = event.page

    this = event.control
    this.disabled = True
    page.update()

    time.sleep(1)

    this.disabled = False
    page.update()
    force_refresh_view(page, _ROUTE)


def cowrire_install_view(page: ft.Page):
    """
    https://github.com/cowrie/cowrie 安装页面
    :param page:
    :return:
    """
    title = 'cowrie installer'
    page.title = title

    # 标题
    title_row = ft.Row(
        controls=[
            ft.Text(
                title.capitalize(),
                size=30,
                weight=ft.FontWeight.BOLD
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # 描述
    desc_container = ft.Container(
        content=ft.Text(
            "Cowrie is a medium to high interaction SSH and Telnet honeypot designed to log brute force attacks "
            "and the shell interaction performed by the attacker. In medium interaction mode (shell) it emulates "
            "a UNIX system in Python, in high interaction mode (proxy) it functions as an SSH and telnet proxy to "
            "observe attacker behavior to another system.",
            size=20,
        ),
        alignment=ft.alignment.center,
        margin=20,
    )

    # 检查是否已安装和运行
    container_exists, container = check_is_alive(_CONTAINER_NAME)
    container_id = container.id if container else None
    alive_status, attach_command = generate_container_alive_status(container_exists, container_id)

    controls = [
        title_row,
        desc_container,
        ft.Divider(),
        alive_status,
    ]
    if attach_command:
        controls.append(attach_command)

    # 添加停止按钮、配置按钮、安装按钮
    events = {
        'configure': configure,
        'stop': stop_event,
        'start': start_event,
    }
    op_buttons = generate_container_op_buttons(container_exists, events)
    controls.append(ft.Divider())
    controls.append(op_buttons)
    controls.append(ft.Divider())

    return ft.Column(
        controls=controls,
        spacing=10,
    )


if __name__ == '__main__':
    pass
