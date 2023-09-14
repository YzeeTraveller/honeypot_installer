#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: views
# @date: 2023/9/14
import time

import flet as ft


def generate_container_alive_status(alive: bool, container_id: str):
    """
    generate_container_alive_status
    :param alive:
    :return:
    """
    alive_status = ft.Row(
        controls=[
            ft.Icon(ft.icons.CHECK_CIRCLE, color='green'),
            ft.Text(
                f'Program is not running, please click the Start button.',
                size=15,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    attach_command = None
    if alive:
        alive_status = ft.Row(
            controls=[
                ft.Icon(ft.icons.CHECK_CIRCLE, color='green'),
                ft.Text(
                    f'Program is running, container id is: {container_id}',
                    size=20,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        attach_command = ft.Row(
            controls=[
                ft.Icon(ft.icons.BOOKMARK, color='green'),
                ft.Text(
                    f'Attach container\'s command: docker exec -it {container_id} sh',
                    size=20,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    return alive_status, attach_command


def generate_container_op_buttons(alive: bool, events: dict):
    """
    generate_container_op_buttons 生成操作按钮组
    :param alive:
    :return:
    """
    buttons = ft.Row(
        controls=[
            ft.VerticalDivider(),
            ft.ElevatedButton(
                icon=ft.icons.FILE_UPLOAD,
                text="Configure",
                on_click=events['configure'],
                disabled=alive,
            ),
            ft.VerticalDivider(),
            ft.ElevatedButton(
                icon=ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED,
                text="Stop",
                disabled=not alive,
                on_click=events['stop']
            ),
            ft.VerticalDivider(),
            ft.ElevatedButton(
                icon=ft.icons.START,
                text="Start",
                disabled=alive,
                on_click=events['start'],
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    return buttons


def force_refresh_view(page: ft.Page, route_name: str):
    """
    force_refresh_view
    :param page:
    :param route_name:
    :return:
    """
    page.route = "/"
    page.update()
    page.route = route_name
    page.update()