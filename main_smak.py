from print_tricks import pt

import os, json, ctypes
import threading
import tkinter as tk
from tkinter import simpledialog, font
from pynput import keyboard
from pynput.keyboard import Key, Controller

from pystray import MenuItem as item, Icon
from PIL import Image
import sys

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Make the root window invisible

    def run(self):
        self.root.mainloop()

class Window1:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.title("Window 1")
        tk.Label(self.window, text="This is Window 1").pack()
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        pt('window')

    def close(self):
        pt('close')
        self.window.destroy()

class Window2:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.title("Window 2")
        tk.Label(self.window, text="This is Window 2").pack()
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        pt('window')

    def close(self):
        pt('close')
        self.window.destroy()

class WindowManager:
    def __init__(self, root):
        self.root = root
        self.window1 = None
        self.window2 = None

    def toggle_window1(self):
        if not self.window1 or not self.window1.window.winfo_exists():
            pt('if')
            self.window1 = Window1(self.root)
        else:
            pt('else')
            self.window1.close()
            self.window1 = None

    def toggle_window2(self):
        if not self.window2 or not self.window2.window.winfo_exists():
            pt('if')
            self.window2 = Window2(self.root)
        else:
            pt('else')
            self.window2.close()
            self.window2 = None


def setup_tray_icon(window_manager):
    def run_icon():
        icon_image = Image.new('RGB', (64, 64), color = 'red')  # Create a red icon
        menu = (
            item('Toggle Window 1', lambda: window_manager.toggle_window1()),
            item('Toggle Window 2', lambda: window_manager.toggle_window2()),
            item('Quit', lambda: icon.stop())
        )
        icon = Icon("Test Tray", icon_image, "Test Tray", menu)
        icon.run()

    icon_thread = threading.Thread(target=run_icon, daemon=True)
    icon_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    main_app = MainWindow(root)
    manager = WindowManager(root)
    
    setup_tray_icon(manager)
    main_app.run()