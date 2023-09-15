#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: cowrie
# @date: 2023/9/14

import json
import os.path
import time

import flet as ft
import yaml

from utils.docker import *
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
_IMAGE_NAME = 'cowrie:latest'
_CONTAINER_NAME = 'cowrie'
_BASE_IMAGE_DIR = os.path.join('vendor', 'cowrie')


def load_configs(page: ft.Page):
    """
    load_configs
    :return:
    """
    settings = page.client_storage.get(_CONTAINER_NAME)
    ret = {"PORT_MAPPING": settings.get("PORT_MAPPING")}
    for entry in page.client_storage.get_keys("COWRIE_"):
        ret[entry] = settings.get(entry)
    _, container = check_is_alive(_CONTAINER_NAME)
    if container:
        for entry in container.attrs['Config']['Env']:
            if entry.startswith("COWRIE_"):
                k, v = entry.split("=")
                ret[k] = v
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

    # 端口配置
    port_bindings = page.client_storage.get("PORT_MAPPING")

    # 传递蜜罐配置（如有）
    env_params = {}
    for entry in page.client_storage.get_keys("COWRIE_"):
        env_params[entry] = page.client_storage.get(entry)

    container = start_container(
        _IMAGE_NAME,
        _CONTAINER_NAME,
        force_remove=True,
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

    alive, _ = check_is_alive(_CONTAINER_NAME)

    def _install_telnet_plugin(event):
        _p: ft.Page = event.page
        _p.client_storage.set("COWRIE_TELNET_ENABLED", "yes")
        _port_mapping = _p.client_storage.get("PORT_MAPPING")
        _port_mapping["2223"] = 2223
        _p.client_storage.set("PORT_MAPPING", _port_mapping)
        _envs = load_configs(_p)
        start_container(_IMAGE_NAME, _CONTAINER_NAME, force_remove=True, ports=_port_mapping, environment=_envs)
        time.sleep(1)
        force_refresh_view(_p, _ROUTE)

    telnet_plugin = ft.ElevatedButton(
        icon=ft.icons.PHONELINK_SETUP,
        text="Install Telnet Plugin",
        on_click=_install_telnet_plugin,
        disabled=not alive,
    )

    mysql_export_plugin = ft.ElevatedButton(
        icon=ft.icons.PHONELINK_SETUP,
        text="Install MySQL Export Plugin",
        on_click=None,
        disabled=not alive,
    )

    es_export_plugin = ft.ElevatedButton(
        icon=ft.icons.PHONELINK_SETUP,
        text="Install Squid TCP Tunnel Plugin",
        on_click=None,
        disabled=not alive,
    )

    return ft.Row(
        controls=[
            telnet_plugin,
            mysql_export_plugin,
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
    )


def build_image_event(event):
    """
    build_image
    :param event:
    :return:
    """
    page: ft.Page = event.page

    build_image(_BASE_IMAGE_DIR, _IMAGE_NAME)
    alert(page, 'success', f'build image success')


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

    # 基础镜像是否已构建
    base_image_exists = check_image_has_built(_IMAGE_NAME)
    image_built_msg = 'Base image has been built.' if base_image_exists else 'Base image has not been built.'
    built_status = ft.Row(
        controls=[
            ft.Icon(ft.icons.CHECK_CIRCLE, color='green' if base_image_exists else 'red'),
            ft.Text(
                image_built_msg,
                size=15,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
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
        built_status,
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
        'build': build_image_event,
        'configure': select_configure,
        'stop': stop_event,
        'start': start_event,
        'export_log': export_log,
    }
    op_buttons = generate_container_op_buttons(container_exists, events, base_image_exists)
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
