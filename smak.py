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
        - bug: can open multiple instances of settings. And the instances then are not closeable. 
            - probably has to do with the mainloop. How do we shut down the mainloop for this and 
            for the main lock screen window? 
        - bug: 
            - Can't disable the lock screen, and then re-enable it again. 
        
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

import os, json, ctypes, threading
import tkinter as tk
from tkinter import simpledialog, font
from pynput import keyboard
from pynput.keyboard import Key, Controller

from pystray import MenuItem as item, Icon, Menu
from PIL import Image
import sys

class SmakStopper:
    positions = [
            "top left", "top center", "top right",
            "center left", "center center", "center right",
            "bottom left", "bottom center", "bottom right"
        ]

    def __init__(self, master, show_password=False, custom_msg=None, position=None, size=12, alpha=0.1):
        pt('init')
        self.master = master
        self.smak_window = tk.Toplevel(self.master)
        
        self.typed_keys = []
        self.password = ['q', 'u', 'i', 't']
        self.show_custom_msg = True
        self.show_password = show_password
        self.custom_msg = custom_msg
        self.position = position

        self.size = size
        self.alpha = alpha
        self.labels = []
        self.listener = None
        
        self.is_running = False  ## might be able to delete these vars
        
        self.load_settings()

    def load_settings(self):
        settings = SettingsUtility.load_settings()
        self.show_custom_msg = settings.get('show_custom_msg', True)
        self.show_password = settings.get('show_password', False)
        self.custom_msg = settings.get('custom_msg', None)
        self.position = settings.get('position', None)
        self.size = settings.get('size', 12)
        self.alpha = settings.get('alpha', 0.1)
        self.password = settings.get('password', ['q', 'u', 'i', 't'])

    def update_settings(self, new_settings):
        self.show_password = new_settings['show_password']
        self.custom_msg = new_settings['custom_msg']
        self.position = new_settings['position']
        self.size = new_settings['size']
        self.alpha = new_settings['alpha']
        self.password = new_settings['password']
        # self.save_settings()
        self.setup_window()

    def setup_window(self):
        if not self.smak_window:
            return
        self.smak_window.title('SMAK Stopper')
        self.smak_window.protocol("WM_DELETE_WINDOW", self.close)

        
        self.smak_window.configure(bg='black')
        # Temporarily unset override-redirect to change fullscreen attribute
        self.smak_window.overrideredirect(False)
        self.smak_window.state('zoomed')
        # self.smak_window.attributes('-fullscreen', True)
        self.smak_window.attributes('-topmost', True)
        # Reapply override-redirect if needed
        self.smak_window.overrideredirect(True)
        self.smak_window.attributes('-alpha', self.alpha)
        if self.show_password:
            self.display_password()

        self.is_running = True
        
    def display_password(self):
        if not self.smak_window:
            return
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
                self.smak_window, text=self.custom_msg,
                fg='white', bg='black', font=custom_font
            )
            x, y = self.position
            label.place(relx=x, rely=y, anchor='center')
            self.labels.append(label)
        else:
            for position in self.positions:
                vertical, horizontal = position.split()
                label = tk.Label(
                    self.smak_window, text=self.custom_msg,
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
        # Suppress keys to prevent them from being processed further by the system
        self.listener = keyboard.Listener(on_press=self.on_press, suppress=True)
        self.listener.start()

    def stop_keyboard_listener(self):
        pt('stop listener')
        if self.listener:
            self.listener.stop()
            self.listener = None

    def on_press(self, key):

        if key == Key.esc and any(k in self.typed_keys for k in [Key.shift, Key.ctrl]):
            return

        ## TODO: Temporary destroy for testing. 
        if hasattr(key, 'char') and key.char == '1':
            ## TODO: Temporary destroy for testing. 
            self.close()

        if hasattr(key, 'char') and key.char:
            key_value = key.char
        else:
            key_value = key

        self.typed_keys.append(key_value)
        if len(self.typed_keys) > len(self.password):
            self.typed_keys = self.typed_keys[-len(self.password):]

        if self.typed_keys == self.password:
            self.close()

    def run(self):
        if not self.is_running:  # Check if the application is not already running
            self.start_keyboard_listener()
            self.setup_window()
    
    def close(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        if self.smak_window and hasattr(self.smak_window, 'tk') and self.smak_window.winfo_exists():
            self.smak_window.destroy()
        self.is_running = False  



class PasswordManager:
    def __init__(self, settings_path):
        self.settings_path = SettingsUtility.get_path()

    def load_settings(self):
        try:
            with open(self.settings_path, 'r') as file:
                settings = json.load(file)
            return settings
        except FileNotFoundError:
            return {}

    def save_settings(self, settings):
        with open(self.settings_path, 'w') as file:
            json.dump(settings, file)

    def validate_password(self, current_password):
        settings = self.load_settings()
        # Assuming the password is stored under the key 'password'
        stored_password = settings.get('password', [])
        return stored_password == list(current_password)

    def change_password(self, new_password, enable_encryption=False):
        settings = self.load_settings()
        if enable_encryption:
            # Add encryption logic here if needed
            encrypted_password = self.encrypt_password(new_password)
            settings['password'] = encrypted_password
        else:
            settings['password'] = list(new_password)
        self.save_settings(settings)

    def encrypt_password(self, password):
        ## TODO: Implement encryption
        return password 

class SettingsUtility:
    
    @staticmethod
    def load_settings():
        settings_path = SettingsUtility.get_path()
        try:
            with open(settings_path, 'r') as file:
                settings = json.load(file)
            return settings
        except FileNotFoundError:
            return {
                'show_custom_msg': True,
                'show_password': False,
                'custom_msg': None,
                'position': None,
                'size': 12,
                'alpha': 0.1,
                'password': ['q', 'u', 'i', 't']
            }
    @staticmethod
    def get_path():
        smak_folder_path = os.path.join(os.path.expanduser('~'), 'Documents', 'SMAK')
        if not os.path.exists(smak_folder_path):
            os.makedirs(smak_folder_path)
        settings_path = os.path.join(smak_folder_path, 'SMAK_settings.json')
        return settings_path

class SettingsDialog:
    def __init__(self, master, smak_app=None, system_tray_app=None):
        self.master = master
        self.smak_app = smak_app
        self.system_tray_app = system_tray_app
        
        self.password_manager = PasswordManager(SettingsUtility.get_path())

        self.settings_window = tk.Toplevel(self.master)
        self.settings_window.title("SMAK Settings")
        
        self.title_font_size = 12
        
        
        # Set the window as modal and focus
        self.settings_window.transient(self.master)  # Set as a transient window of the master window
        self.settings_window.grab_set()  # Modal
        self.settings_window.focus_set()  # Focus
        self.settings_window.attributes('-topmost', True)
        
        # Setup window contents
        self.load_settings()
        self.setup_window_contents()
        
        ## Set DPI awareness (No longer necessary, but will be more seamless/integrated)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    
    def close(self):
        # Properly release the grab and destroy the window
        self.settings_window.grab_release()
        self.settings_window.destroy()
        if self.system_tray_app:
            self.system_tray_app.settings_win_inst = None
    
    def load_settings(self):
        self.settings = SettingsUtility.load_settings()
        if self.settings is None:
            self.settings = {
                'show_custom_msg': True,
                'show_password': False,
                'custom_msg': None,
                'position': None,
                'size': 12,
                'alpha': 0.1,
                'password': ['q', 'u', 'i', 't']
            }
    
    def setup_window_contents(self):
        self.setup_window_appearance()
        self.setup_message_display_options()
        self.setup_password_section()
        
        self.save_button = tk.Button(self.settings_window, text="Save Settings", command=self.save_settings)
        self.save_button.pack()
        
        self.settings_window.update()
        self.center_window()
        # self.settings_window.update()
    
    def get_screen_size(self):
        
        hdc = ctypes.windll.user32.GetDC(None)
        
        width = ctypes.windll.gdi32.GetDeviceCaps(hdc, 118)  ## 118 is HORZRES
        height = ctypes.windll.gdi32.GetDeviceCaps(hdc, 117)  ## 117 is VERTRES
        
        ctypes.windll.user32.ReleaseDC(None, hdc)
        
        return width, height
    
    def center_window(self):
        pt("center_window")
        w, h = self.get_screen_size()
        size = tuple(int(_) for _ in self.settings_window.geometry().split('+')[0].split('x'))
        x = (w // 2) - (size[0] // 2)
        y = (h // 2) - (size[1] // 2)
        self.settings_window.geometry("+{}+{}".format(x, y))
        pt(w,h,x,y)

    def setup_window_appearance(self):
        #########################################################
        ## Invisible Window Appearance
        #########################################################
        window_section_label = tk.Label(
            self.settings_window, text="Invisible Window Appearance", 
            font=("Helvetica", self.title_font_size, "bold"))
        window_section_label.pack(pady=(10, 5))
    
        ###################
        ## Alpha Transparency
        ###################
        if self.settings is None:
            return  # or load settings again or set default values
        
        self.alpha_label = tk.Label(self.settings_window, text="Alpha (Transparency):").pack()
        self.alpha_entry = tk.Entry(self.settings_window)
        self.alpha_entry.insert(0, str(self.settings['alpha']))
        self.alpha_entry.pack()

    def setup_message_display_options(self):
        #########################################################
        ## Message Message Options
        #########################################################
        window_section_label = tk.Label(
            self.settings_window, text="Display Message", 
            font=("Helvetica", self.title_font_size, "bold"))
        window_section_label.pack(pady=(10, 5))

        ###################
        ## show password or custom message Radio Buttons
        ###################        # Variable to hold the display option
        self.display_option_var = tk.IntVar()
        self.display_option_var.set(1 if self.settings['show_password'] else 2)

        ## Frame for 2 radio buttons
        radio_frame = tk.Frame(self.settings_window)
        radio_frame.pack()

        self.radio_password = tk.Radiobutton(
            radio_frame, text="Show password on lock screen", variable=self.display_option_var, value=1)
        self.radio_password.pack(side=tk.TOP, anchor='w')  # Anchor west to align the buttons

        self.radio_custom_msg = tk.Radiobutton(
            radio_frame, text="Show custom message:", variable=self.display_option_var, value=2)
        self.radio_custom_msg.pack(side=tk.TOP, anchor='w')  # Anchor west to align the buttons

        ## Custom Message Entry (only enabled if custom message option is selected)
        custom_msg = self.settings['custom_msg'] if self.settings['custom_msg'] is not None else ''
        self.custom_msg_entry = tk.Entry(self.settings_window)
        self.custom_msg_entry.insert(0, custom_msg)
        self.custom_msg_entry.pack()
        self.custom_msg_entry.config(state='normal' if self.display_option_var.get() == 2 else 'disabled')

        ## Update the state of the custom message entry based on these radio button selection
        self.radio_password.config(command=self.update_display_option)
        self.radio_custom_msg.config(command=self.update_display_option)


        ###################
        ## Font Size
        ###################
        self.size_label = tk.Label(self.settings_window, text="Font Size:")
        self.size_label.pack(pady=(10, 0))
        self.size_entry = tk.Entry(self.settings_window)
        self.size_entry.insert(0, str(self.settings['size']))
        self.size_entry.pack()
        
        ###################
        ## Positions to display Unlock message(s)
        ###################
        positions_title_label = tk.Label(self.settings_window, text="Message Location:")
        positions_title_label.pack(pady=(10, 0))

        
        
        self.position_entry = tk.Entry(self.settings_window)
        if self.settings['position']:
            self.position_entry.insert(0, f"{self.settings['position'][0]}, {self.settings['position'][1]}")
        self.position_entry.pack()

        locations_label = tk.Label(self.settings_window, 
            text="(type in a single location,\nor leave blank for all locations at once)")
        locations_label.pack(pady=(0, 2))  

        possible_locations_label = tk.Label(self.settings_window, 
            text="Possible Locations:")
        possible_locations_label.pack(pady=(0, 2))  
        
        positions_rows = [
            SmakStopper.positions[:3],  ## First row (top positions)
            SmakStopper.positions[3:6], ## Second row (center positions)
            SmakStopper.positions[6:]   ## Third row (bottom positions)
        ]
        

        for i, row in enumerate(positions_rows):
            if i == 0:  # First row
                text = '(' + ', '.join(row)
            elif i == len(positions_rows) - 1:  # Last row
                text = ', '.join(row) + ')'
            else:
                text = ', '.join(row)
            
            position_row_label = tk.Label(self.settings_window, text=text)
            position_row_label.pack()

    def setup_password_section(self):
        #########################################################
        ## Password Section
        #########################################################
        
        
        password_section_label = tk.Label(
            self.settings_window, 
            text="Password Management", 
            font=("Helvetica", self.title_font_size, "bold"))
        password_section_label.pack(pady=(10, 5))

        ## Current Password
        self.current_password_label = tk.Label(self.settings_window, text="Current Password:")
        self.current_password_label.pack()
        self.current_password_entry = tk.Entry(self.settings_window, show="*")
        self.current_password_entry.pack()

        ## New Password
        self.new_password_label = tk.Label(self.settings_window, text="New Password:")
        self.new_password_label.pack()
        self.new_password_entry = tk.Entry(self.settings_window, show="*")
        self.new_password_entry.pack()

        ## Confirm New Password
        self.confirm_password_label = tk.Label(self.settings_window, text="Confirm New Password:")
        self.confirm_password_label.pack()
        self.confirm_password_entry = tk.Entry(self.settings_window, show="*")
        self.confirm_password_entry.pack()

        ## Enable Encryption
        self.enable_encryption_var = tk.BooleanVar(value=False)
        self.enable_encryption_checkbox = tk.Checkbutton(self.settings_window, text="Encrypt Password", variable=self.enable_encryption_var)
        self.enable_encryption_checkbox.pack()

    def update_display_option(self):
        if self.display_option_var.get() == 1:
            self.custom_msg_entry.config(state='disabled')
        else:
            self.custom_msg_entry.config(state='normal')

    def save_settings(self):
        # Validate and save new password if provided
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        enable_encryption = self.enable_encryption_var.get()

        if new_password and new_password == confirm_password:
            if self.password_manager.validate_password(current_password):
                self.password_manager.change_password(new_password, enable_encryption)
            else:
                tk.messagebox.showerror("Error", "Current password is incorrect.")
        elif new_password:
            tk.messagebox.showerror("Error", "New passwords do not match.")

        # Collect all other settings from the dialog
        try:
            position_input = self.position_entry.get().strip()
            if position_input:
                position = tuple(map(float, position_input.split(',')))
            else:
                position = None

            new_settings = {
                'show_password': self.display_option_var.get() == 1,
                'show_custom_msg': self.display_option_var.get() == 2,
                'custom_msg': self.custom_msg_entry.get() if self.display_option_var.get() == 2 else None,
                'position': position,
                'size': int(self.size_entry.get()),
                'alpha': float(self.alpha_entry.get()),
            }
            # Save settings to file
            self.password_manager.save_settings(new_settings)

            # Update SmakStopper instance if it is active
            if self.smak_app:
                self.smak_app.update_settings(new_settings)

            self.close()
            
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input for position. Please enter two comma-separated numbers.")


class MainTKLoop:
    def __init__(self, root) -> None:
        self.root = root
        # self.root.withdraw()

    def run(self):
        self.root.mainloop()    


class WindowManager:
    def __init__(self, root):
        self.root = root
        self.window1 = None
        self.window2 = None

    def toggle_window1(self):
        if not self.window1 or not self.window1.smak_window.winfo_exists():

            self.window1 = SmakStopper(master=self.root)
            self.window1.run()
        else:
            self.window1.close()
            self.window1 = None

    def toggle_window2(self):
        if not self.window2 or not self.window2.settings_window.winfo_exists():
            self.window2 = SettingsDialog(master=self.root, smak_app=self.window1)
        else:
            self.window2.close()
            self.window2 = None


def setup_tray_icon(window_manager, main_app):
    def quit_app(icon):
        icon.stop()  # Stop the pystray icon
        main_app.quit()  # Quit the main Tkinter application

    icon_image = Image.new('RGB', (64, 64), color = 'red')  # Create a red icon
    menu = (
        item('__SMAK STOPPER__', lambda: None),
        Menu.SEPARATOR,
        item('Lock the Screen', lambda: window_manager.toggle_window1()),
        item('Settings', lambda: window_manager.toggle_window2()),
        item('Quit', lambda: quit_app(icon))
    )
    icon = Icon("Test Tray", icon_image, "Test Tray", menu)
    icon.run()
    
    # def quit(self):
    #     if self.icon:
    #         self.icon.stop()
    #     if self.app:
    #         self.app.close()
    #     sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    main_loop = MainTKLoop(root)
    manager = WindowManager(root)
    
    systray = True
    if systray:
        icon_thread = threading.Thread(
            target=setup_tray_icon,
            args=(manager, main_loop),
            daemon=True)
        icon_thread.start()
    else:
        app = SmakStopper(root, show_password=True)
        app.run()
        
    main_loop.run()




