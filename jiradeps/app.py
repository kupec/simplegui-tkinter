import asyncio
from functools import partial

import httpx
from loguru import logger
from pydantic import BaseModel
import tkinter as tk
from tkinter import ttk
from typing import Callable
import yarl

from jiradeps.async_worker import async_task
from jiradeps.settings import Settings, get_settings, save_settings


setting_keys = ['jira_project', 'jira_epic_jql']


SettingsDataVars = dict[str, tk.StringVar]

class AppModel:
    settings_data_vars: SettingsDataVars = dict()

class Issue(BaseModel):
    key: str
    summary: str
    description: str

app_model = AppModel()

@async_task
async def app(root: tk.Tk):
    loader_frame = create_loader_frame(root)
    settings = await get_settings()
    for key, value in settings:
        app_model.settings_data_vars[key] = tk.StringVar(value=value)

    loader_frame.destroy()
    create_main_frame(root)


def create_loader_frame(root: tk.Tk) -> ttk.Frame:
    frame = ttk.Frame(root, padding=50)
    frame.grid()
    ttk.Label(frame, text='Loading...').grid(column=0, row=0)
    return frame


def create_main_frame(root: tk.Tk) -> ttk.Frame:
    frame = ttk.Frame(root, padding=8)
    frame.grid()

    create_main_menu(root)

    loading_label = ttk.Label(frame, text='Loading...')
    loading_label.grid(column=0, row=0)

    @async_task
    async def on_mount():
        try:
            issues = await load_issues()
        except:
            loading_label['text'] = 'Cannot fetch issues'
        else:
            loading_label.destroy()

            issue_selector = ttk.Combobox(
                frame,
                width=200,
                values=[f'{issue.key} {issue.summary}' for issue in issues]
            )
            issue_selector.grid(column=0, row=0)
            issue_selector.set(issue_selector['values'][0])

    on_mount()

    return frame


@logger.catch(reraise=True)
async def load_issues():
    settings = await get_settings()
    base_url = yarl.URL(settings.jira_base_url)
    async with httpx.AsyncClient() as client:
        response = await client.post(str(base_url / 'rest/api/2/search'))
        data = response.json()

    return [Issue(**issue_data, **issue_data['fields']) for issue_data in data['issues']]

def create_main_menu(root: tk.Tk):
    root.option_add('*tearOff', False)
    menubar = tk.Menu(root)

    menu_file = tk.Menu(menubar)
    menu_file.add_command(label='Settings...', command=partial(
        create_settings_window,
        root,
    ))
    menu_file.add_command(label='Exit', command=root.destroy)
    menubar.add_cascade(label='App', menu=menu_file)

    root['menu'] = menubar


def create_settings_window(root: tk.Tk):
    window = tk.Toplevel(root)
    window.title('Settings')

    frame = ttk.Frame(window)
    frame.grid()

    next_settings_data_vars = dict()
    for index, (key, value) in enumerate(app_model.settings_data_vars.items()):
        data_var = tk.StringVar(value=value.get())
        next_settings_data_vars[key] = data_var

        ttk.Label(frame, text=f'{key} = ').grid(column=0, row=index)
        ttk.Entry(frame, textvariable=data_var).grid(column=1, row=index)

    ttk.Button(
        frame,
        text='Save',
        command=partial(
            handle_save_settings,
            next_settings_data_vars,
            on_close=window.destroy,
        ),
    ).grid(column=0, row=len(setting_keys))
    ttk.Button(
        frame,
        text='Cancel',
        command=window.destroy,
    ).grid(column=1, row=len(setting_keys))


@async_task
async def handle_save_settings(next_settings_data_vars: SettingsDataVars, on_close: Callable):
    next_settings = Settings(**{
        key: value.get()
        for key, value in next_settings_data_vars.items()
    })
    await save_settings(next_settings)

    for key, value in next_settings_data_vars.items():
        app_model.settings_data_vars[key].set(value.get())

    on_close()
