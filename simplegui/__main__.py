import tkinter as tk

from simplegui.app import app
from simplegui.async_worker import start_async_worker


start_async_worker()

root = tk.Tk()
app(root)
root.mainloop()
