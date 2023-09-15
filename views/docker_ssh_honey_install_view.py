#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: honeyd_install_view
# @date: 2023/9/14

import json
import os.path
import random
import re
import time
import traceback

import flet as ft

import docker
import yaml

from utils.docker import *
from utils.project import (
    get_project_root,
)
from utils.views import *

_ROUTE = '/install/ssh_honey'
_IMAGE_NAME = 'txt3rob/docker-ssh-honey'
_CONTAINER_NAME = 'ssh_honey'
_BASE_IMAGE_DIR = os.path.join('vendor', 'ssh_honey')


def load_configs(page: ft.Page):
    """
    load_configs
    :return:
    """
    settings = page.client_storage.get(_CONTAINER_NAME)
    ret = {"PORT_MAPPING": settings.get("PORT_MAPPING")}
    for entry in settings.keys():
        ret[entry] = settings.get(entry)
    _, container = check_is_alive(_CONTAINER_NAME)
    if container:
        for entry in container.attrs['Config']['Env']:
            if len(entry.split("=")) == 2:
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
    configs = load_configs(page)
    port_bindings = configs.get("PORT_MAPPING")

    # 传递蜜罐配置（如有）
    env_params = {}
    for entry in configs.keys():
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

        path = os.path.join('uploads', uf.name)
        with open(path, 'r', encoding='utf-8') as f:
            c = yaml.load(f, Loader=yaml.FullLoader)

        settings = {}
        for entry in c:
            value = c[entry]
            page.client_storage.set(entry, value)
            settings[entry] = value
        page.client_storage.set(_CONTAINER_NAME, settings)
        page.update()

    force_refresh_view(page, _ROUTE)


def select_env_configure(event):
    """
    选择环境相关配置
    :return:
    """
    page = event.page

    pick_files_dialog = ft.FilePicker(
        on_result=parse_configure_file
    )
    page.overlay.append(pick_files_dialog)
    page.update()
    pick_files_dialog.pick_files('select env config file', allow_multiple=False)
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
    log_path = os.path.join(assets_dir, 'ssh-honeypot.log')
    src_path = '/ssh-honeypot/ssh-honeypot.log'
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

    alive, container = check_is_alive(_CONTAINER_NAME)

    new_ports = [20020, 20028]

    def _add_new_ssh_service(e):
        """
        _add_new_ssh_service
        :param e:
        :return:
        """
        _p: ft.Page = e.page
        settings = load_configs(_p)

        port_bindings = settings.get("PORT_MAPPING")

        port = dropdown.value.split(':')
        internal_port = int(port[0])
        host_port = int(port[1])

        command = f'/bin/ssh-honeypot -u root -i 1 -p {internal_port} -l ssh-honeypot.log &'
        exec_command(container, command, tty=True)

        port_bindings[internal_port] = host_port
        settings["PORT_MAPPING"] = port_bindings

        _p.client_storage.set(_CONTAINER_NAME, settings)
        alert(_p, 'success', f'add new ssh service success, port: ssh -p {host_port} root@127.0.01')

    activte_ports = []
    for line in exec_command_output(container, 'ps -ef | grep ssh-honeypot'):
        match = re.findall('-p (\d+) -', line)
        if match:
            port = int(match[0])
            activte_ports.append(port)

    dropdown = ft.Dropdown(
        label="Port",
        hint_text="Choose your new ssh port",
        options=[
            ft.dropdown.Option(
                str(i) + ":" + str(i),
            ) for i in range(new_ports[0], new_ports[1]) if i not in activte_ports
        ],
        autofocus=True,
    )

    add_new_ssh_service_btn = ft.ElevatedButton(
        icon=ft.icons.ADD,
        text="Add new ssh service",
        disabled=not alive,
        on_click=_add_new_ssh_service,
    )

    add_service_group = ft.Row(
        controls=[
            dropdown,
            add_new_ssh_service_btn,
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    connect_ssh_board = [
        ft.Row(
            controls=[
                ft.ElevatedButton(
                    f'ssh -p {port} root@127.0.01',
                    on_click=lambda e: e.page.set_clipboard(f'ssh -p {port} root@127.0.01') or short_alert(e.page, 'success', 'copy success')
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ) for port in activte_ports if port != 22
    ]

    controls = [
        add_service_group,
        ft.Row(
            controls=[
                ft.Text(
                    value="Active ssh service",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    ]
    controls.extend(connect_ssh_board)

    return ft.Column(
        controls=controls,
        spacing=30,
        alignment=ft.MainAxisAlignment.CENTER,
    )


def build_image_event(event):
    """
    build_image
    :param event:
    :return:
    """
    page: ft.Page = event.page

    envs = load_configs(page)

    start_container(_IMAGE_NAME, _CONTAINER_NAME, force_remove=True, environment=envs)
    alert(page, 'success', f'build image success')


def docker_ssh_honey_install_view(page: ft.Page):
    """
    安装页面
    :param page:
    :return:
    """
    title = 'docker-ssh-honey'
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
            "This program listens for incoming ssh connections and logs the ip address, username, and password used."
            " This was written to gather rudimentary intelligence on brute force attacks.",
            size=20,
        ),
        alignment=ft.alignment.center,
        margin=20,
    )

    docuement_row = ft.Row(
        controls=[
            ft.ElevatedButton(
                'Document',
                icon=ft.icons.HELP,
                on_click=lambda event: event.page.launch_url(
                    'https://github.com/random-robbie/docker-ssh-honey')
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    config_title = ft.Row(
        controls=[
            ft.Text(
                'Environment variables',
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

    # 检查是否已安装和运行
    container_exists, container = check_is_alive(_CONTAINER_NAME)
    container_id = container.id if container else None
    alive_status, attach_command = generate_container_alive_status(container_exists, container_id)

    controls = [
        title_row,
        desc_container,
        docuement_row,
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
        'configure': select_env_configure,
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
                'Others',
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
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


if __name__ == '__main__':
    pass
