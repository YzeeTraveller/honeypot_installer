#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: run
# @date: 2023/9/14

import os.path

import flet as ft
import yaml

from views.cowrie_install_view import cowrire_install_view
from views.dionaea_install_view import dionaea_install_view
from views.docker_ssh_honey_install_view import docker_ssh_honey_install_view
from utils.docker import is_docker_installed


DEFAULT_CONFIGS_DIR = 'environment_configs'

SOURCE_CONFIG = {
    'cowrie': {
        'name': 'Cowrie',
        'url': 'https://github.com/cowrie/cowrie'
    },
    'ssh_honey': {
        'name': 'ssh_honey',
        'url': 'https://github.com/random-robbie/docker-ssh-honey',
    },
    'dionaea': {
        'name': 'Dionaea',
        'url': 'https://github.com/DinoTools/dionaea'
    }
}

UPLOAD_DIR = 'uploads'

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def generate_menu_button(source_name: str, disabled: bool):
    """
    生成菜单按钮
    :return:
    """
    def _on_click(event: ft.ControlEvent):
        """
        on_click
        :param event:
        :return:
        """
        event.page.go(f"/install/{source_name}")

    text = f"Install {source_name}."
    tooltip = SOURCE_CONFIG[source_name]['url']

    button_row = ft.Row(
        controls=[
            ft.ElevatedButton(
                text=text,
                tooltip=tooltip,
                on_click=_on_click,
                disabled=disabled
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    return button_row


def index_view(page: ft.Page):
    """
    index_view

    主页面
    :return:
    """
    title = 'Honeypot Program Installer'
    author = 'Created By @XiaoMing'
    page.title = title

    # 标题行
    title_row = ft.Row(
        controls=[
            ft.Text(title, size=30, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    # 作者行
    author_row = ft.Row(
        controls=[
            ft.Text(author, size=20, text_align=ft.TextAlign.CENTER),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # docker是否安装
    docker_installed = is_docker_installed()
    docker_installed_row = ft.Row(
        controls=[
            ft.Icon('check_circle', color='green'),
            ft.Text(
                'Docker has installed.',
                size=15,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    if not docker_installed:
        docker_installed_row = ft.Row(
            controls=[
                ft.Icon('cancel', color='red'),
                ft.Text(
                    'Docker is not installed, Please read the document to install docker: ',
                    size=15,
                ),
                ft.ElevatedButton(
                    text='Document',
                    style=ft.ButtonStyle(
                        shape=ft.ContinuousRectangleBorder(radius=30),
                        color=ft.colors.GREEN_800
                    ),
                    url='https://docs.docker.com/engine/install/',
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    # 菜单栏
    menu_text = 'Select One Program to install'
    menu_text_row = ft.Row(
        controls=[
            ft.Text(menu_text, size=20, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.Column(
        controls=[
            title_row,
            author_row,
            ft.Divider(),
            menu_text_row,
            docker_installed_row,
            generate_menu_button('cowrie', not docker_installed),
            generate_menu_button('dionaea', not docker_installed),
            generate_menu_button('ssh_honey', not docker_installed),
        ],
        spacing=30
    )


def init_default_configs(page: ft.Page):
    """
    init_default_configs
    :return:
    """
    for key in SOURCE_CONFIG.keys():
        config_path = os.path.join(DEFAULT_CONFIGS_DIR, f"{key}.yaml")
        if not os.path.exists(config_path):
            continue
        with open(config_path, 'r', encoding='utf-8') as f:
            c = yaml.load(f, Loader=yaml.FullLoader)
        settings = {}
        for entry in c:
            value = c[entry]
            settings[entry] = value
        page.client_storage.set(key, settings)


def run(page: ft.Page):
    """
    runq
    :param page:
    :return:
    """
    init_default_configs(page)

    page.title = "Routes Example"
    page.auto_scroll = True

    def route_change(route: ft.RouteChangeEvent):
        """
        route_change
        :param route:
        :return:
        """
        print(page.route)

        page.views.clear()

        page.views.append(
            ft.View(
                "/",
                [
                    index_view(page)
                ],
            )
        )
        if page.route == "/":
            pass
        elif page.route == '/install/cowrie':
            page.views.append(
                ft.View(
                    "/install/cowrie",
                    [
                        cowrire_install_view(page)
                    ],
                )
            )
        elif page.route == '/install/ssh_honey':
            page.views.append(
                ft.View(
                    "/install/ssh_honey",
                    [
                        docker_ssh_honey_install_view(page)
                    ],
                )
            )
        elif page.route == '/install/dionaea':
            page.views.append(
                ft.View(
                    "/install/dionaea",
                    [
                        dionaea_install_view(page)
                    ],
                )
            )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


def main():
    """
    main
    :return:
    """
    ft.app(
        target=run,
        view=ft.AppView.WEB_BROWSER,
        assets_dir='assets',
        upload_dir='uploads',
    )


if __name__ == '__main__':
    main()
