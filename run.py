#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: run
# @date: 2023/9/14

"""

source:

1. https://github.com/cowrie/cowrie
2. https://github.com/DataSoft/Honeyd
3. https://github.com/DinoTools/dionaea

"""

import flet as ft

from views.cowrie_install_view import cowrire_install_view

from utils.docker import is_docker_installed


SOURCE_CONFIG = {
    'cowrie': {
        'name': 'Cowrie',
        'url': 'https://github.com/cowrie/cowrie'
    },
    'honeyd': {
        'name': 'Honeyd',
        'url': 'https://github.com/DataSoft/Honeyd',
    },
    'dionaea': {
        'name': 'Dionaea',
        'url': 'https://github.com/DinoTools/dionaea'
    }
}


def generate_menu_button(source_name: str, disabled: bool):
    """
    生成菜单按钮
    :return:
    """
    def _on_click(event):
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
            generate_menu_button('honeyd', not docker_installed),
            generate_menu_button('dionaea', not docker_installed)
        ],
        spacing=30
    )


def run(page: ft.Page):
    page.title = "Routes Example"

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
                    "/",
                    [
                        cowrire_install_view(page)
                    ],
                )
            )
        elif page.route == '/install/honeyd':
            pass
        elif page.route == '/install/dionaea':
            pass

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
    ft.app(target=run, view=ft.AppView.WEB_BROWSER)


if __name__ == '__main__':
    main()
