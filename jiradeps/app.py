from functools import partial

import tkinter as tk
from tkinter import ttk
from typing import Callable

from jiradeps.async_worker import async_task
from jiradeps.settings import Settings, get_settings, save_settings


setting_keys = ['jira_project', 'jira_epic_jql']

@async_task
async def app(root: tk.Tk):
    loader_window = create_loader_frame(root)
    settings = await get_settings()

    loader_window.destroy()
    create_main_frame(root, settings)


def create_loader_frame(root: tk.Tk) -> ttk.Frame:
    frame = ttk.Frame(root, padding=50)
    frame.grid()
    ttk.Label(frame, text='Loading...').grid(column=0, row=0)
    frame.pack()
    return frame


def create_main_frame(root: tk.Tk, settings: Settings) -> ttk.Frame:
    frame = ttk.Frame(root, padding=8)
    frame.grid()

    for index, key in enumerate(setting_keys):
        ttk.Label(frame, text=f'{key} = ').grid(column=0, row=index)

        value = getattr(settings, key)
        ttk.Label(frame, text=value).grid(column=1, row=index)

    create_main_menu(root, settings)

    frame.pack()
    return frame

def create_main_menu(root: tk.Tk, settings: Settings):
    root.option_add('*tearOff', False)
    menubar = tk.Menu(root)

    menu_file = tk.Menu(menubar)
    menu_file.add_command(label='Settings...', command=partial(
        create_settings_window,
        root,
        settings,
    ))
    menu_file.add_command(label='Exit', command=root.destroy)
    menubar.add_cascade(label='App', menu=menu_file)

    root['menu'] = menubar


def create_settings_window(root: tk.Tk, settings: Settings):
    window = tk.Toplevel(root)
    window.title('Settings')

    frame = ttk.Frame(window)
    frame.grid()

    settings_values: dict[str, tk.StringVar] = dict()
    for index, key in enumerate(setting_keys):
        ttk.Label(frame, text=f'{key} = ').grid(column=0, row=index)

        data_var = tk.StringVar(value=getattr(settings, key))
        settings_values[key] = data_var
        ttk.Entry(frame, textvariable=data_var).grid(column=1, row=index)

    ttk.Button(
        frame,
        text='Save',
        command=partial(
            handle_save_settings,
            settings_values,
            on_close=window.destroy,
        ),
    ).grid(column=0, row=len(setting_keys))
    ttk.Button(
        frame,
        text='Cancel',
        command=window.destroy,
    ).grid(column=1, row=len(setting_keys))

    frame.pack()

@async_task
async def handle_save_settings(settings_values: dict[str, tk.StringVar], on_close: Callable):
    next_settings = Settings(**{
        key: value.get()
        for key, value in settings_values.items()
    })
    await save_settings(next_settings)

    on_close()
