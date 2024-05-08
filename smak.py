'''TODO
    Encrypted Passwords:
        - Experiment with an actual encrypted system
        
    All settings changeable:
        - Password currently not changeable. 
        - Custom font, 
        - custom position will fail, at least if using text. 
    
    Auto Lock:
        - After x minutes/seconds/hours, have this auto-lock the screen. 
        
    systray icon
        - Integrate by default with a systray icon. 
        - But keep it optional to not have a systray icon (if its loaded via another systray app
        like the edge engine systray app).
        - Also allow some settings to be changeable from a systray menu
        
    EXE
        - Make this into an optional exe. 
        
    Startup with windows
        - Figure this out:
        - CMD & therefore maybe the startup command:
            python smak.py --systray
        
    Real Icon:
        - Maybe a babies hand with a rattle, smashing the keyboard. 
        - This is from a larger image where maybe a cat's paw is also on the keyboard? 
    
    Readme:
        - Make it a humorous readme. Maybe ask for help with this? 
        
    Pypi:
        - Upload to pypi
        - give the pypi and the github the picture, an icon. 
    
    '''
from print_tricks import pt

import os, json
import tkinter as tk
from tkinter import simpledialog, font
from pynput import keyboard
from pynput.keyboard import Key, Controller

from pystray import MenuItem as item, Icon
from PIL import Image
import sys

class SmakLocker:
    def __init__(self, show_password=False, custom_msg=None, position=None, size=12, alpha=0.1):
        smak_folder_path = os.path.join(os.path.expanduser('~'), 'Documents', 'SMAK')
        if not os.path.exists(smak_folder_path):
            os.makedirs(smak_folder_path)
        self.settings_path = os.path.join(smak_folder_path, 'SMAK_settings.json')
        
        
        self.root = tk.Tk()
        self.root.title('SMAK Locker')
        self.typed_keys = []
        self.password = ['q', 'u', 'i', 't']
        self.show_password = show_password
        self.custom_msg = custom_msg
        self.position = position
        self.positions = [
            "top left", "top center", "top right",
            "center left", "center center", "center right",
            "bottom left", "bottom center", "bottom right"
        ]
        self.size = size
        self.alpha = alpha
        self.labels = []
        self.listener = None
        
        self.load_settings()
        

    def load_settings(self):
        try:
            with open(self.settings_path, 'r') as file:
                settings = json.load(file)
            self.show_password = settings.get('show_password', False)
            self.custom_msg = settings.get('custom_msg', None)
            self.position = settings.get('position', None)
            self.size = settings.get('size', 12)
            self.alpha = settings.get('alpha', 0.1)
            self.password = settings.get('password', ['q', 'u', 'i', 't'])
        except FileNotFoundError:
            self.show_password = False
            self.custom_msg = None
            self.position = None
            self.size = 12
            self.alpha = 0.1
            self.password = ['q', 'u', 'i', 't']

    def save_settings(self):
        settings = {
            'show_password': self.show_password,
            'custom_msg': self.custom_msg,
            'position': self.position,
            'size': self.size,
            'alpha': self.alpha,
            'password': self.password
        }
        with open(self.settings_path, 'w') as file:
            json.dump(settings, file)

    def update_settings(self, new_settings):
        self.show_password = new_settings['show_password']
        self.custom_msg = new_settings['custom_msg']
        self.position = new_settings['position']
        self.size = new_settings['size']
        self.alpha = new_settings['alpha']
        self.password = new_settings['password']
        self.save_settings()
        self.setup_window()

    def setup_window(self):
        self.root.configure(bg='black')
        # Temporarily unset override-redirect to change fullscreen attribute
        self.root.overrideredirect(False)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        # Reapply override-redirect if needed
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', self.alpha)
        if self.show_password:
            self.display_password()

    def display_password(self):
        # Clear existing labels if any
        if hasattr(self, 'labels'):
            for label in self.labels:
                label.destroy()
        else:
            self.labels = []
        
        custom_font = font.Font(family="Helvetica", size=self.size, weight="bold", underline=1)
        
        password = ''.join(self.password)
        self.custom_msg = f'Type in "{password}" (without quotes) to unlock the screen'
            
        if self.position:
            label = tk.Label(
                self.root, text=self.custom_msg,
                fg='white', bg='black', font=custom_font
            )
            x, y = self.position
            label.place(relx=x, rely=y, anchor='center')
            self.labels.append(label)
        else:
            for position in self.positions:
                vertical, horizontal = position.split()
                label = tk.Label(
                    self.root, text=self.custom_msg,
                    fg='white', bg='black', font=custom_font
                )
                if vertical == 'top':
                    y = 0.1
                elif vertical == 'center':
                    y = 0.5
                else:  # bottom
                    y = 0.9
                
                if horizontal == 'left':
                    x = 0.1
                elif horizontal == 'center':
                    x = 0.5
                else:  # right
                    x = 0.9
                
                label.place(relx=x, rely=y, anchor='center')
                self.labels.append(label)
                
    def start_keyboard_listener(self):
        pt('start listener')
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()


    def stop_keyboard_listener(self):
        pt('stop listener')
        if self.listener:
            self.listener.stop()
            self.listener = None

    def on_press(self, key):
        if hasattr(key, 'char') and key.char:
            key_value = key.char
        else:
            key_value = key

        self.typed_keys.append(key_value)
        if len(self.typed_keys) > len(self.password):
            self.typed_keys = self.typed_keys[-len(self.password):]

        if self.typed_keys == self.password:
            self.root.destroy()

        if key == Key.esc and any(k in self.typed_keys for k in [Key.shift, Key.ctrl]):
            self.root.destroy()
            
    def change_password(self):
        self.stop_keyboard_listener()  # Stop listening while dialog is open
        self.root.attributes('-topmost', False)
        
        new_sequence = simpledialog.askstring("Input", "Enter new unlock sequence:", parent=self.root)
        
        self.root.attributes('-topmost', True)
        
        if new_sequence:
            self.password = list(new_sequence)
            self.display_password()
        
        self.root.focus_force()
        self.start_keyboard_listener()  # Restart listening after dialog is closed

    def open_settings_dialog(self):
        self.stop_keyboard_listener()  # Stop listening while dialog is open
        self.root.attributes('-topmost', False)
        initial_settings = {
            'show_password': self.show_password,
            'custom_msg': self.custom_msg,
            'position': self.position,
            'size': self.size,
            'alpha': self.alpha
        }
        settings_dialog = SettingsDialog(self, self.root, initial_settings)
        self.root.wait_window(settings_dialog.top)
        self.root.attributes('-topmost', True)
        self.root.deiconify()
        self.root.focus_force()
        self.start_keyboard_listener()  # Restart listening after dialog is closed

    def run(self):
        self.start_keyboard_listener()
        self.setup_window()
        self.root.mainloop()


    def run_systray(self):

        # Create an image for the systray icon (1x1 black square)
        icon_image = Image.new('RGB', (64, 64), 'black')
        menu = (
            item('Lock', self.show_lock_screen),
            item('Settings', self.open_settings_dialog),
            item('Quit', self.quit_systray)
        )
        icon = Icon("SmakLocker", icon_image, "SmakLocker", menu)
        icon.run()

    def show_lock_screen(self):
        self.root.deiconify()

    def quit_systray(self, icon):
        icon.stop()
        sys.exit()


        
class SettingsDialog:
    def __init__(self, smak_locker, master, initial_settings):
        self.smak_locker = smak_locker
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("SMAK Settings")
        self.settings = initial_settings

        ###################
        ## Focus the window, Capture all input. Aka "Modal" 
        ###################
        self.top.transient(master)
        self.top.grab_set()
        self.top.focus_set()
        
        ###################
        ## Center the window
        ###################
        self.top.update_idletasks()  # Update internal states
        w = self.top.winfo_screenwidth()
        h = self.top.winfo_screenheight()
        size = tuple(int(_) for _ in self.top.geometry().split('+')[0].split('x'))
        x = w // 2 - size[0] // 2
        y = h // 2 - size[1] // 2
        self.top.geometry("+{}+{}".format(x, y))



        ###################
        ## Display Password
        ###################
        self.show_password_var = tk.BooleanVar(value=self.settings['show_password'])
        self.show_password_checkbox = tk.Checkbutton(self.top, text="Display Unlock Code", variable=self.show_password_var)
        self.show_password_checkbox.pack()

        ###################
        ## Custom Message
        ###################
        self.custom_msg_label = tk.Label(self.top, text="Custom Message:")
        self.custom_msg_label.pack()
        self.custom_msg_entry = tk.Entry(self.top)
        self.custom_msg_entry.insert(0, self.settings['custom_msg'])
        self.custom_msg_entry.pack()

        ###################
        ## Positions
        ###################
        positions_title_label = tk.Label(self.top, text="Positions:")
        positions_title_label.pack()
        
        positions_rows = [
            self.smak_locker.positions[:3],  ## First row (top positions)
            self.smak_locker.positions[3:6], ## Second row (center positions)
            self.smak_locker.positions[6:]   ## Third row (bottom positions)
        ]
        
        for row in positions_rows:
            position_row_label = tk.Label(self.top, text=', '.join(row))
            position_row_label.pack()
            
        self.position_entry = tk.Entry(self.top)
        if self.settings['position']:
            self.position_entry.insert(0, f"{self.settings['position'][0]}, {self.settings['position'][1]}")
        self.position_entry.pack()

        ###################
        ## Fint Size
        ###################
        self.size_label = tk.Label(self.top, text="Font Size:")
        self.size_label.pack()
        self.size_entry = tk.Entry(self.top)
        self.size_entry.insert(0, str(self.settings['size']))
        self.size_entry.pack()

        ###################
        ## Alpha Transparency
        ###################
        self.alpha_label = tk.Label(self.top, text="Alpha (Transparency):")
        self.alpha_label.pack()
        self.alpha_entry = tk.Entry(self.top)
        self.alpha_entry.insert(0, str(self.settings['alpha']))
        self.alpha_entry.pack()

        ###################
        ## Save Button
        ###################
        self.save_button = tk.Button(self.top, text="Save Settings", command=self.save_settings)
        self.save_button.pack()

        ###################
        ## Close window
        ###################
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

    def save_settings(self):
        try:
            position_input = self.position_entry.get().strip()
            if position_input:
                position = tuple(map(float, position_input.split(',')))
            else:
                position = None

            new_settings = {
                'show_password': self.show_password_var.get(),
                'custom_msg': self.custom_msg_entry.get(),
                'position': position,
                'size': int(self.size_entry.get()),
                'alpha': float(self.alpha_entry.get()),
                'password': self.smak_locker.password  # Assuming password is managed elsewhere
            }
            self.smak_locker.update_settings(new_settings)
            self.on_close()
            
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input for position. Please enter two comma-separated numbers.")

    def on_close(self):
        self.top.destroy()
        self.master.deiconify()  
        self.master.focus_force()


if __name__ == "__main__":
    app = SmakLocker(show_password=True)
    # app.change_password()
    # app.open_settings_dialog()
    systray = True
    if systray:
        app.run_systray()
    else:
        app.run()

