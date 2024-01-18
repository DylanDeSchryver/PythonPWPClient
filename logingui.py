import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk
from PIL import Image
from sql_program import *
import requests
import datetime
import os
import numpy as np
import cv2
import threading

# Global variables
user_info = {'name': '', 'last_name': '', 'username': '', 'password': ''}


log_text = None

#Function to send commands to the robot
def send_command(direction):
    ip = '192.168.1.30'
    url = f'http://192.168.1.30:4200/move'
    data = {'direction': direction}

    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"Command '{direction}' sent successfully.")
    else:
        print(f"Failed to send command '{direction}'")

# Function to update camera feed
def update_camera_feed():
    try:
        response = requests.get('http://192.168.1.30:4200/camera', stream=True)

        if response.status_code == 200:
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_tk = ImageTk.PhotoImage(Image.fromarray(image))

            camera_feed_label.configure(image=image_tk)
            camera_feed_label.image = image_tk

    except Exception as e:
        print(f"Error updating camera feed: {e}")

    root.after(100, update_camera_feed)

# Main window
def window():
    global windows
    windows = Tk()
    windows.geometry("600x400")
    windows.title("Window")
    windows.configure(bg="#ffffff")

    label2 = Label(windows, text="Login or create an account.")
    label2.pack()

    add_button = Button(windows, text='Create an Account', command=create)
    add_button.pack()

    login_button = Button(windows, text='Login', command=login)
    login_button.pack()

    exit_button = Button(windows, text='Save and Exit', command=windows.destroy)
    exit_button.pack()

    windows.mainloop()

# Create account window
def create():
    global creates
    global windows
    global name_entry, last_entry, user_entry, passw_entry
    windows.destroy()

    creates = Tk()
    creates.geometry("600x400")
    creates.title("Create an Account")
    creates.configure(bg='white')

    name = Label(creates, text="Name: ")
    name.pack()

    name_entry = Entry(creates)
    name_entry.pack()

    last = Label(creates, text="Last Name: ")
    last.pack()

    last_entry = Entry(creates)
    last_entry.pack()

    user = Label(creates, text="User: ")
    user.pack()

    user_entry = Entry(creates)
    user_entry.pack()

    passw = Label(creates, text="Password: ")
    passw.pack()

    passw_entry = Entry(creates, show='*')
    passw_entry.pack()

    save_button = Button(creates, text='Save and Exit', command=lambda:[save_info(),window()])
    save_button.pack()

    creates.mainloop()

# Save user information to global variables and run save_sql()
def save_info():
    global creates
    global user_info, name_entry, last_entry, user_entry, passw_entry
    user_info['name'] = name_entry.get()
    user_info['last_name'] = last_entry.get()
    user_info['username'] = user_entry.get()
    user_info['password'] = passw_entry.get()
    save_sql()
    creates.destroy()

# Login window
def login():
    global logins
    global windows
    global userlogin_entry, passwlogin_entry
    windows.destroy()
    global root
    logins = Tk()
    logins.geometry("600x400")
    logins.title("Log In")

    user = Label(logins, text="User: ")
    user.pack()

    userlogin_entry = Entry(logins)
    userlogin_entry.pack()

    passw = Label(logins, text="Password: ")
    passw.pack()

    passwlogin_entry = Entry(logins, show='*')
    passwlogin_entry.pack()

    login_button = Button(logins, text='Log In', command=check_login)
    login_button.pack()

# Check if the username and password are correct
def check_login():
    global logins
    global userlogin_entry, passwlogin_entry

    username = userlogin_entry.get()
    password = passwlogin_entry.get()
    key = get_sql(username, password)

    if key:
        logins.destroy()
        name = first(username, password)
        loggedin(username, password, key, name)
    else:
        messagebox.showerror('Error', "Incorrect Username or Password.")
        logins.destroy()

# Logged-in window
def loggedin(username, password, key, name):
    global log_text, camera_feed_label, root

    root = tk.Tk()
    root.geometry("800x600")
    root.title("Logged In")

    top_left_frame = tk.Frame(root, bg="white", width=400, height=300)
    top_right_frame = tk.Frame(root, bg="black", width=400, height=300)
    bottom_left_frame = tk.Frame(root, width=400, height=300, bg='pink')
    bottom_right_frame = tk.Frame(root, width=400, height=300)

    top_left_frame.grid(row=0, column=0, sticky="nsew")
    camera_feed_label = tk.Label(top_left_frame)
    camera_feed_label.pack()
    bottom_left_frame.grid(row=1, column=0, sticky="nsew")

    top_right_frame.grid(row=0, column=1, sticky="nsew")
    bottom_right_frame.grid(row=1, column=1, sticky="nsew")

    log_text = tk.Text(bottom_right_frame, wrap="word", bg="black", fg="white")
    log_text.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(bottom_right_frame, command=log_text.yview)
    scrollbar.pack(side="right", fill="y")
    log_text.config(yscrollcommand=scrollbar.set)

    update_camera_feed()

    forward_button = tk.Button(
        top_right_frame,
        text="   ^   \nForward",
        command=lambda: [send_command('forward'),forward()]
    )

    backward_button = tk.Button(
        top_right_frame,
        text="Backward\n   v   ",
        command=lambda: [send_command('backward'),backward()]
    )

    left_button = tk.Button(
        top_right_frame,
        text="<   Left",
        command=lambda: [send_command('left'),left()]
    )

    right_button = tk.Button(
        top_right_frame,
        text="Right   >",
        command=lambda: [send_command('right'),right()]
    )

    stop_button = tk.Button(
        top_right_frame,
        text="   Stop   ",
        command=lambda: [send_command('stop'),stop()]
    )

    logout_button = tk.Button(top_right_frame, text="   Logout   ", command=lambda: [logout()])

    forward_button.grid(row=0, column=1)
    backward_button.grid(row=2, column=1)
    left_button.grid(row=1, column=0)
    right_button.grid(row=1, column=2)
    stop_button.grid(row=1, column=1)
    logout_button.grid(row=2, column=2)

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    current_time = datetime.datetime.now()
    today = current_time.strftime("%x")
    today_time = current_time.strftime("%X").replace(':', '꞉')
    filename = f"{username} {today} {today_time}.txt"
    today = today.replace('/', '-')
    script_directory = os.path.dirname(__file__)
    filename = f"{script_directory}\\{username} {today} {today_time}.txt"

    with open(filename, 'w') as f:
        f.write(f'New Log File @{username}!')
        print("log created")

    def forward():
        current_time = datetime.datetime.now()

        today = current_time.strftime("%x")
        today_time = current_time.strftime("%X")
        today = today.replace('/', '-')
        log_message(f'\n{username}/Move Forward {today} {today_time}')
        with open(filename, 'at') as f:
            f.write(f'\n{username}/Move Forward {today} {today_time}')

    def backward():
        current_time = datetime.datetime.now()

        today = current_time.strftime("%x")
        today_time = current_time.strftime("%X")
        today = today.replace('/', '-')
        log_message(f'\n{username}/Move Backward {today} {today_time}')
        with open(filename, 'at') as f:
            f.write(f'\n{username}/Move Backward {today} {today_time}')

    def left():
        current_time = datetime.datetime.now()

        today = current_time.strftime("%x")
        today_time = current_time.strftime("%X")
        today = today.replace('/', '-')
        log_message(f'\n{username}/Turn Left {today} {today_time}')
        with open(filename, 'at') as f:
            f.write(f'\n{username}/Turn Left {today} {today_time}')

    def right():
        current_time = datetime.datetime.now()

        today = current_time.strftime("%x")
        today_time = current_time.strftime("%X")
        today = today.replace('/', '-')
        log_message(f'\n{username}/Turn Right {today} {today_time}')
        with open(filename, 'at') as f:
            f.write(f'\n{username}/Turn Right {today} {today_time}')

    def stop():
        current_time = datetime.datetime.now()

        today = current_time.strftime("%x")
        today_time = current_time.strftime("%X")
        today = today.replace('/', '-')
        log_message(f'\n{username}/Stop {today} {today_time}')
        with open(filename, 'at') as f:
            f.write(f'\n{username}/Stop {today} {today_time}')

    def logout():
        #global log_text
        current_time = datetime.datetime.now()

        root.destroy()
        today = current_time.strftime("%x")
        today_time = current_time.strftime("%X")
        today = today.replace('/', '-')
        #log_message(f'\n{username}/Logout {today} {today_time}')
        with open(filename, 'at') as f:
            f.write(f'\n{username}/Logout {today} {today_time}')
        window()

    def log_message(message):
        current_text = log_text.get("1.0", tk.END)
        new_text = f"{message}\n{current_text}"
        log_text.delete("1.0", tk.END)
        log_text.insert("1.0", new_text)

    def welcome():
        log_text.insert("1.0", f"\nWelcome {name}\n")

    welcome()

    root.mainloop()

# Save window
def save():
    global root
    root = Tk()
    root.geometry("600x400")
    root.title("Save and Exit")
    label3 = Label(root, text="")
    label3.pack()
    button = Button(root, text='Save and Exit', command=exit)
    button.pack()

if __name__ == '__main__':
    window()
