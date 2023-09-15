#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: dionaea_install_view
# @date: 2023/9/14

import json
import os.path
import time
import traceback

import flet as ft

import docker
import yaml

from utils.docker import *
from utils.project import *
from utils.views import *

_ROUTE = '/install/dionaea'
_IMAGE_NAME = 'dinotools/dionaea'
_CONTAINER_NAME = 'dionaea'
_BASE_IMAGE_DIR = os.path.join('vendor', 'dionaea')


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

    # 传递环境变量
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

    alert(page, 'success', f'start success, container id: {container.id}')

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
    log_path = os.path.join(assets_dir, 'dionaea.log')
    src_path = '/opt/dionaea/var/log/dionaea/dionaea.log'
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

    plugin_overwrite_dir = os.path.join(get_project_root(), 'plugin_overwrite_configs')
    plugin_config_dir = os.path.join(get_project_root(), 'plugin_configs')
    alive, container = check_is_alive(_CONTAINER_NAME)

    def _install_log_db_plugin(event):
        _p: ft.Page = event.page

        _c = read_yaml_file(os.path.join(plugin_config_dir, 'dionaea_db_sql.yaml'))
        sqlite_path = 'sqlite:////opt/dionaea/var/lib/dionaea/dionaea.sqlite'
        _c[0]['config']['url'] = sqlite_path
        overwrite_path = os.path.join(plugin_overwrite_dir, 'log_db_sql.yaml')
        with open(overwrite_path, 'w') as f:
            yaml.dump(_c, f)
        # overwrite plugin config
        push_files(container, overwrite_path, '/opt/dionaea/etc/dionaea/ihandlers-available')
        # restart services
        start_container(_IMAGE_NAME, _CONTAINER_NAME, reload=True)
        # pull files
        alert(_p, 'success', 'install log db plugin success.')

    log_db_plugin = ft.ElevatedButton(
        icon=ft.icons.PHONELINK_SETUP,
        text="Install Log Db Plugin",
        on_click=_install_log_db_plugin,
        disabled=not alive,
    )

    def _export_db_file(event):
        """

        :param event:
        :return:
        """
        page = event.page
        assets_db_file_path = os.path.join(get_project_root(), 'assets', 'dionaea.sqlite')
        db_ori_path = '/opt/dionaea/var/lib/dionaea/dionaea.sqlite'
        success = True
        try:
            export_files(container, db_ori_path, assets_db_file_path)
        except:
            success = False
        msg = f'export success, file path: {assets_db_file_path}' if success else 'export failed.'
        alert(page, 'export result', msg)

    export_db_plugin = ft.ElevatedButton(
        icon=ft.icons.IMPORT_EXPORT,
        text="Export Plugin Db Log",
        on_click=_export_db_file,
        disabled=not alive,
    )

    def _install_ftp_plugin(event):
        _p: ft.Page = event.page

        _c = read_yaml_file(os.path.join(plugin_config_dir, 'dionaea_ftp.yaml'))
        overwrite_path = os.path.join(plugin_overwrite_dir, 'ftp.yaml')
        with open(overwrite_path, 'w') as f:
            yaml.dump(_c, f)
        # overwrite plugin config
        push_files(container, overwrite_path, '/opt/dionaea/etc/dionaea/services-available')
        # restart services
        start_container(_IMAGE_NAME, _CONTAINER_NAME, reload=True)
        # pull files
        alert(_p, 'success', 'install ftp plugin success.')

    ftp_install_plugin = ft.ElevatedButton(
        icon=ft.icons.PHONELINK_SETUP,
        text="Install ftp Plugin",
        on_click=_install_ftp_plugin,
        disabled=not alive,
    )

    return ft.Row(
        controls=[
            log_db_plugin,
            export_db_plugin,
            ftp_install_plugin,
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


def dionaea_install_view(page: ft.Page):
    """
    https://github.com/cowrie/cowrie 安装页面
    :param page:
    :return:
    """
    title = 'dionaea installer'
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
            "Dionaea is meant to be a nepenthes successor, embedding python as scripting language, using libemu to "
            "detect shellcodes, supporting ipv6 and tls.",
            size=20,
        ),
        alignment=ft.alignment.center,
        margin=20,
    )

    config_title = ft.Row(
        controls=[
            ft.Text(
                'Environment Variables',
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

    docuement_row = ft.Row(
        controls=[
            ft.ElevatedButton(
                'Document',
                icon=ft.icons.HELP,
                on_click=lambda event: event.page.launch_url('https://dionaea.readthedocs.io/en/latest/introduction.html')
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
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
