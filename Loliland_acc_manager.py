import flet as ft
import time
import json
import os
import subprocess

from connection import cursor, conn

os.system('cls')

def main(page: ft.Page):
    # Настройки главной страницы приложения
    page.title="Loliland manager"
    page.theme_mode='dark'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height=480
    page.window.width=300
    page.window.resizable=False
    page.window.maximizable=False

    selected_row_index = None
    launcher_path = None

    # Путь к лаунчеру
    cursor.execute('SELECT link FROM launcherlink')
    launcher_path = cursor.fetchone()
    if launcher_path:
        launcher_path = launcher_path[0]
    else:
        launcher_path = None

    # Таблица
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text('Accounts:')),
        ],
        rows=[],
        width=page.window.width,
        data_text_style=ft.TextStyle(size=14),
        heading_text_style=ft.TextStyle(size=18),
    )

    # Функция для обработки выбора строки
    def select_row(row_index):
        nonlocal selected_row_index

        # Сбрасываем стиль предыдущей выбранной строки
        if selected_row_index is not None:
            table.rows[selected_row_index].color = None  # Убираем выделение

        # Выделяем новую строку
        selected_row_index = row_index
        table.rows[row_index].color = ft.Colors.BLUE_500  # Изменяем цвет фона строки

        table.update()  # Обновляем таблицу

    username_field = ft.TextField(width=page.window.width-80)
    password_field = ft.TextField(width=page.window.width-80, password=True)
    error_text = ft.Text('', width=page.window.width, text_align='center')

    # Получение пользователей
    def update_table():
        cursor.execute('SELECT username FROM accounts')
        users = cursor.fetchall()
        table.rows = []
        for user in users:
            row_index = len(table.rows)  # Индекс новой строки
            table.rows.append(ft.DataRow([ft.DataCell(ft.Text(user[0]))], on_select_changed=lambda e, idx=row_index: select_row(idx),))  # Обработчик выбора строки))

    update_table()

    def clear_fields():
        username_field.value = ''
        password_field.value = ''
        page.update()

    # Добавить аккаунт
    def add_account(e):
        if password_field.value and username_field.value:
            cursor.execute('SELECT * FROM accounts WHERE username = ?', (username_field.value, ))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO accounts (username, password) VALUES (?, ?)', (username_field.value, password_field.value, ))
                conn.commit()
                error_text.value='Account was added'
                clear_fields()
                update_table()
                time.sleep(1.4)
                error_text.value=''
                main_page(e)
            else:
                error_text.value='Account already exists'
                clear_fields()
                page.update()
        else:
            error_text.value='Please fill in all fields'
            page.update()

    # Удалить аккаунт
    def delete_account(e):
        nonlocal selected_row_index
        if selected_row_index is not None or selected_row_index == 0:
            cursor.execute('DELETE FROM accounts WHERE username = ?', (table.rows[selected_row_index].cells[0].content.value, ))
            conn.commit()
            selected_row_index=None
            update_table()
            page.update()
        else:
            error_text.value='Please select an account to delete'

    # Получить путь
    def get_path(e: ft.FilePickerResultEvent):
        nonlocal launcher_path
        error_text.value=''
        page.update()
        if e.files:
            launcher_path = e.files[0].path
            if launcher_path.endswith('LoliLand.exe'):
                cursor.execute('SELECT link FROM launcherlink')
                launcher_link = cursor.fetchone()
                if launcher_link:
                    cursor.execute('UPDATE launcherlink SET link = ? WHERE id = ?', (launcher_path, 1, ))
                    conn.commit()
                    error_text.value='Launcher path updated'
                    page.update()
                    time.sleep(1.5)
                    error_text.value=''
                    page.update()
                else:
                    cursor.execute('INSERT INTO launcherlink (link) VALUES (?)', (launcher_path, ))
                    conn.commit()
                    error_text.value='Launcher path added'
                    page.update()
                    time.sleep(1.5)
                    error_text.value=''
                    page.update()
            else:
                error_text.value='Please select Loliland.exe'
                page.update()
        else:
            error_text.value='Path not selected'
            page.update()

    file_picker = ft.FilePicker(on_result=get_path)

    user_folder = os.environ["USERPROFILE"]
    # Пустая страница
    def start(e):
        if selected_row_index is not None or selected_row_index == 0:
            if launcher_path:
                if os.path.isfile(launcher_path):
                    cursor.execute('SELECT username, password FROM accounts WHERE username = ?', (table.rows[selected_row_index].cells[0].content.value, ))
                    user_data = cursor.fetchone()
                    nonlocal user_folder
                    with open(rf'{user_folder}\loliland\auth.json', 'w', encoding='utf-8') as file:
                        json.dump({'login': str(user_data[0]), 'password': str(user_data[1])}, file, indent=4, ensure_ascii=False)
                    app_path = launcher_path
                    error_text.value=''
                    page.update()
                    subprocess.run(app_path)
                else:
                    error_text.value='Launcher path not found'
                    page.update()
            else:
                error_text.value='Please select launcher'
                page.update()
        else:
            error_text.value='Please select an account to start'
            page.update()
    
    # Вызов главной страницы
    def main_page(e):
        page.clean()
        page.add(
            ft.Column(
                [
                    table,
                    ft.Row(
                        [
                            ft.ElevatedButton('Add', on_click=add_page),
                            ft.ElevatedButton('Delete', on_click=delete_account),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        width=page.window.width
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton('Get launcher', on_click=lambda _: file_picker.pick_files(allow_multiple=False, dialog_title='Select LoliLand.exe'))  ,
                            ft.ElevatedButton('Start', on_click=start)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        width=page.window.width
                    ),
                    error_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    # Страница добавления
    def add_page(e):
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text('Username', size=20, text_align='center', width=page.window.width),
                    username_field,
                    ft.Text('Password', size=20, text_align='center', width=page.window.width),
                    password_field,
                    ft.Row(
                        [
                            ft.ElevatedButton('Add', on_click=add_account),
                            ft.ElevatedButton('Cancel', on_click=main_page)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        width=page.window.width
                    ),
                    error_text
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    
    page.overlay.append(file_picker)

    # Разметка главной страницы приложения
    page.add(
        ft.Column(
            [
                table,
                ft.Row(
                    [
                        ft.ElevatedButton('Add', on_click=add_page),
                        ft.ElevatedButton('Delete', on_click=delete_account),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=page.window.width
                ),
                ft.Row(
                    [
                        ft.ElevatedButton('Get launcher', on_click=lambda _: file_picker.pick_files(allow_multiple=False, dialog_title='Select LoliLand.exe'))  ,
                        ft.ElevatedButton('Start', on_click=start)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=page.window.width
                ),
                error_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(target=main)