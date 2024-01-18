from tkinter import *
from tkinter import messagebox
from logingui import window
import os

file_path = "USER.db"

if not os.path.exists(file_path):
    open(file_path, 'w').close()

window() #call window function