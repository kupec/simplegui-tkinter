from functools import partial
import tkinter as tk
from tkinter import ttk

import httpx

from jiradeps.async_worker import async_task


@async_task
async def make_req(data):
    data.set('requesting...')
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get('http://127.0.0.1:3000/')
            resp = resp.json()
        data.set(resp['message'])
    except Exception:
        data.set('error')


def app(root):
    frm = ttk.Frame(root, padding=50)
    frm.grid()

    data = tk.StringVar()
    data.set("No data")
    ttk.Label(frm, textvariable=data).grid(column=1, row=0)
    ttk.Button(frm, text="Request", command=partial(make_req, data)).grid(column=0, row=0)

    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1)
