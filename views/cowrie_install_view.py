#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: cowrie
# @date: 2023/9/14
import json
import os.path
import time
import traceback

import flet as ft

import docker
import yaml

from utils.docker import (
    check_is_alive,
    export_files,
    stop_and_remove_container,
)
from utils.project import (
    get_project_root,
)
from utils.views import (
    alert,
    force_refresh_view,
    generate_container_alive_status,
    generate_container_op_buttons,
)

_ROUTE = '/install/cowrie'
_IMAGE_NAME = 'cowrie/cowrie:latest'
_CONTAINER_NAME = 'cowire'


def load_configs(page: ft.Page):
    """
    load_configs
    :return:
    """
    ret = {"PORT_MAPPING": page.client_storage.get("PORT_MAPPING")}
    for entry in page.client_storage.get_keys("COWRIE_"):
        ret[entry] = page.client_storage.get(entry)
    return ret


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
        page.client_storage.clear()

        path = os.path.join('uploads', uf.name)
        with open(path, 'r', encoding='utf-8') as f:
            c = yaml.load(f, Loader=yaml.FullLoader)
        for entry in c:
            value = c[entry]
            page.client_storage.set(entry, value)
        page.update()
        os.remove(path)

    force_refresh_view(page, _ROUTE)


def select_configure(event):
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


def export_log(event):
    """
    export log 导出日志
    :param event:
    :return:
    """
    page: ft.Page = event.page

    this: ft.ElevatedButton = event.control

    project_root = get_project_root()
    assets_dir = os.path.join(project_root, 'assets')
    log_path = os.path.join(assets_dir, 'cowrie.json')
    src_path = '/cowrie/cowrie-git/var/log/cowrie/cowrie.json'
    exists, container = check_is_alive(_CONTAINER_NAME)
    if container:
        this.disabled = True
        page.update()
        export_files(container, src_path, log_path)
        this.disabled = False
        page.update()

    if os.path.join(log_path):
        alert(page, 'success', f'export log success, path: {log_path}')
    else:
        alert(page, 'error', f'export log failed')


def install_other_tools(event):
    """
    install_other_tools 安装其他工具
    :param event:
    :return:
    """
    telnet_plugin = ft.ElevatedButton(
        icon=ft.icons.PHONELINK_SETUP,
        text="Install Telnet Plugin",
        on_click=None,
    )

    mysql_export_plugin = ft.ElevatedButton(
        icon=ft.icons.PHONELINK_SETUP,
        text="Install MySQL Export Plugin",
        on_click=None,
    )

    return ft.Row(
        controls=[
            telnet_plugin,
            mysql_export_plugin,
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
    )


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

    config_title = ft.Row(
        controls=[
            ft.Text(
                'Configurations',
                size=30,
                weight=ft.FontWeight.BOLD
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    config_str = json.dumps(load_configs(page))
    config_container = ft.Container(
        content=ft.Text(
            config_str,
            size=20,
        ),
        alignment=ft.alignment.center,
        margin=30,
        bgcolor=ft.colors.GREY_50
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

    controls.extend([
        ft.Divider(),
        config_title,
        config_container,
    ])

    # 添加停止按钮、配置按钮、安装按钮
    op_title = ft.Row(
        controls=[
            ft.Text(
                'Operations',
                size=30,
                weight=ft.FontWeight.BOLD
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    events = {
        'configure': select_configure,
        'stop': stop_event,
        'start': start_event,
        'export_log': export_log,
    }
    op_buttons = generate_container_op_buttons(container_exists, events)
    controls.append(ft.Divider())
    controls.append(op_title)
    controls.append(op_buttons)
    controls.append(ft.Divider())

    # 添加安装其他功能按钮
    install_title = ft.Row(
        controls=[
            ft.Text(
                'Plugins install',
                size=30,
                weight=ft.FontWeight.BOLD
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    controls.append(install_title)
    controls.append(install_other_tools(page))

    return ft.Column(
        controls=controls,
        spacing=40,
    )


if __name__ == '__main__':
    pass
