import tkinter as tk

from loguru import logger

from jiradeps.app import app
from jiradeps.async_worker import start_async_worker


start_async_worker()

logger.info('Starting tkinter')
root = tk.Tk(baseName='Jira deps')
app(root)

logger.info('tkinter is ready')
root.mainloop()
