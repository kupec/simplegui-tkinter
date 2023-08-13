import tkinter as tk

from jiradeps.app import app
from jiradeps.async_worker import start_async_worker


start_async_worker()

root = tk.Tk()
app(root)
root.mainloop()
