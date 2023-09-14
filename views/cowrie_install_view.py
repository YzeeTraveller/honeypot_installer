#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: cowrie
# @date: 2023/9/14
import os.path
import time
import traceback

import flet as ft

import docker
import yaml

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
    page: ft.Page = event.page

    this: ft.ElevatedButton = event.control
    this.disabled = True
    page.update()

    client = docker.from_env()
    container_name = _CONTAINER_NAME
    image_name = _IMAGE_NAME

    # 端口配置
    port_bindings = page.client_storage.get("PORT_MAPPING")

    # 传递蜜罐配置（如有）
    env_params = {}
    for entry in page.client_storage.get_keys("COWRIE_"):
        env_params[entry] = page.client_storage.get(entry)

    container = client.containers.run(
        image=image_name,
        name=container_name,
        detach=True,
        ports=port_bindings,
        environment=env_params,
    )

    this.disabled = False
    page.update()
    time.sleep(1)
    force_refresh_view(page, _ROUTE)

    return container.id


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


def parse_configure_file(e: ft.FilePickerResultEvent):
    """
    parse_configure_file
    :param e:
    :return:
    """
    page = e.page
    control = e.control

    if control.result is not None and control.result.files:
        uf = control.result.files[0]
        upload_url = page.get_upload_url(uf.name, 30)
        control.upload(
            [
                ft.FilePickerUploadFile(
                    uf.name,
                    upload_url=upload_url,
                )
            ]
        )

        path = os.path.join('uploads', uf.name)
        with open(path, 'r', encoding='utf-8') as f:
            c = yaml.load(f, Loader=yaml.FullLoader)
        for entry in c:
            value = c[entry]
            page.client_storage.set(entry, value)

    # force_refresh_view(page, _ROUTE)


def configure(event):
    """
    选择配置
    :return:
    """
    page = event.page

    pick_files_dialog = ft.FilePicker(
        on_result=parse_configure_file
    )
    page.overlay.append(pick_files_dialog)
    page.update()
    pick_files_dialog.pick_files('select configure file', allow_multiple=False)
    page.update()


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
        'export_log': None,
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
