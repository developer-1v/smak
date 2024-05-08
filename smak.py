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

import os, json, ctypes
import tkinter as tk
from tkinter import simpledialog, font
from pynput import keyboard
from pynput.keyboard import Key, Controller

from pystray import MenuItem as item, Icon
from PIL import Image
import sys

class SmakLocker:
    positions = [
            "top left", "top center", "top right",
            "center left", "center center", "center right",
            "bottom left", "bottom center", "bottom right"
        ]
    
    def __init__(self, show_password=False, custom_msg=None, position=None, size=12, alpha=0.1):
        self.root = tk.Tk()

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
        
        self.load_settings()

    def load_settings(self):
        smak_folder_path = os.path.join(os.path.expanduser('~'), 'Documents', 'SMAK')
        if not os.path.exists(smak_folder_path):
            os.makedirs(smak_folder_path)
        self.settings_path = os.path.join(smak_folder_path, 'SMAK_settings.json')
        
        try:
            with open(self.settings_path, 'r') as file:
                settings = json.load(file)
            self.show_custom_msg = settings.get('show_custom_msg', True)
            self.show_password = settings.get('show_password', False)
            self.custom_msg = settings.get('custom_msg', None)
            self.position = settings.get('position', None)
            self.size = settings.get('size', 12)
            self.alpha = settings.get('alpha', 0.1)
            self.password = settings.get('password', ['q', 'u', 'i', 't'])
        except FileNotFoundError:
            self.show_custom_msg = True
            self.show_password = False
            self.custom_msg = None
            self.position = None
            self.size = 12
            self.alpha = 0.1
            self.password = ['q', 'u', 'i', 't']

    def save_settings(self):
        settings = {
            'show_custom_msg': self.show_custom_msg,
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
        self.root.title('SMAK Locker')
        
        self.root.configure(bg='black')
        # Temporarily unset override-redirect to change fullscreen attribute
        self.root.overrideredirect(False)
        self.root.state('zoomed')
        # self.root.attributes('-fullscreen', True)
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
            'show_custom_msg': self.show_custom_msg,
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
            item('Lock', self.run),
            item('Settings', self.open_settings_dialog),
            item('Quit', self.quit_systray)
        )
        self.icon = Icon("SmakLocker", icon_image, "SmakLocker", menu)
        self.icon.run()

    def quit_systray(self):
        self.icon.stop()
        sys.exit()


        
class SettingsDialog:
    def __init__(self, smak_locker, master, initial_settings):
        self.smak_locker = smak_locker
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("SMAK Settings")
        self.settings = initial_settings
        
        self.title_font_size = 12

        ###################
        ## Focus the window, Capture all input. Aka "Modal" 
        ###################
        self.top.transient(master)
        self.top.grab_set()
        self.top.focus_set()
        
        self.setup_window_contents()

        
    def setup_window_contents(self):
        
        self.setup_window_appearance()
        self.setup_message_display_options()
        self.setup_password_section()
        
        
        ###################
        ## Save Button
        ###################
        self.save_button = tk.Button(self.top, text="Save Settings", command=self.save_settings)
        self.save_button.pack()

        ###################
        ## Center the window
        ###################
        self.center_window()
        
        ###################
        ## Close window
        ###################
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_screen_size(self):
        ## Set DPI awareness (No longer necessary, but will be more seamless/integrated)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        hdc = ctypes.windll.user32.GetDC(None)

        width = ctypes.windll.gdi32.GetDeviceCaps(hdc, 118)  ## 118 is HORZRES
        height = ctypes.windll.gdi32.GetDeviceCaps(hdc, 117)  ## 117 is VERTRES

        ctypes.windll.user32.ReleaseDC(None, hdc)

        return width, height

    def center_window(self):
        ###################
        ## Center the window based on its center
        ###################
        
        self.top.update()  # Update internal states
        w, h = self.get_screen_size()
        size = tuple(int(_) for _ in self.top.geometry().split('+')[0].split('x'))
        x = (w // 2) - (size[0] // 2)
        y = (h // 2) - (size[1] // 2)
        self.top.geometry("+{}+{}".format(x, y))
        pt(w, h, size, x, y)
        
    def setup_window_appearance(self):
        #########################################################
        ## Invisible Window Appearance
        #########################################################
        window_section_label = tk.Label(
            self.top, text="Invisible Window Appearance", 
            font=("Helvetica", self.title_font_size, "bold"))
        window_section_label.pack(pady=(10, 5))
    
        ###################
        ## Alpha Transparency
        ###################
        self.alpha_label = tk.Label(self.top, text="Alpha (Transparency):").pack()
        self.alpha_entry = tk.Entry(self.top)
        self.alpha_entry.insert(0, str(self.settings['alpha']))
        self.alpha_entry.pack()
    
    def setup_message_display_options(self):
        #########################################################
        ## Message Message Options
        #########################################################
        window_section_label = tk.Label(
            self.top, text="Display Message", 
            font=("Helvetica", self.title_font_size, "bold"))
        window_section_label.pack(pady=(10, 5))

        ###################
        ## show password or custom message Radio Buttons
        ###################        # Variable to hold the display option
        self.display_option_var = tk.IntVar()
        self.display_option_var.set(1 if self.settings['show_password'] else 2)

        ## Frame for 2 radio buttons
        radio_frame = tk.Frame(self.top)
        radio_frame.pack()

        self.radio_password = tk.Radiobutton(
            radio_frame, text="Show password on lock screen", variable=self.display_option_var, value=1)
        self.radio_password.pack(side=tk.TOP, anchor='w')  # Anchor west to align the buttons

        self.radio_custom_msg = tk.Radiobutton(
            radio_frame, text="Show custom message:", variable=self.display_option_var, value=2)
        self.radio_custom_msg.pack(side=tk.TOP, anchor='w')  # Anchor west to align the buttons

        ## Custom Message Entry (only enabled if custom message option is selected)
        self.custom_msg_entry = tk.Entry(self.top)
        self.custom_msg_entry.insert(0, self.settings['custom_msg'])
        self.custom_msg_entry.pack()
        self.custom_msg_entry.config(state='normal' if self.display_option_var.get() == 2 else 'disabled')

        ## Update the state of the custom message entry based on these radio button selection
        self.radio_password.config(command=self.update_display_option)
        self.radio_custom_msg.config(command=self.update_display_option)


        ###################
        ## Font Size
        ###################
        self.size_label = tk.Label(self.top, text="Font Size:")
        self.size_label.pack(pady=(10, 0))
        self.size_entry = tk.Entry(self.top)
        self.size_entry.insert(0, str(self.settings['size']))
        self.size_entry.pack()
        
        ###################
        ## Positions to display Unlock message(s)
        ###################
        positions_title_label = tk.Label(self.top, text="Message Location:")
        positions_title_label.pack(pady=(10, 0))

        
        
        self.position_entry = tk.Entry(self.top)
        if self.settings['position']:
            self.position_entry.insert(0, f"{self.settings['position'][0]}, {self.settings['position'][1]}")
        self.position_entry.pack()

        locations_label = tk.Label(self.top, 
            text="(type in a single location,\nor leave blank for all locations at once)")
        locations_label.pack(pady=(0, 2))  

        possible_locations_label = tk.Label(self.top, 
            text="Possible Locations:")
        possible_locations_label.pack(pady=(0, 2))  
        
        positions_rows = [
            SmakLocker.positions[:3],  ## First row (top positions)
            SmakLocker.positions[3:6], ## Second row (center positions)
            SmakLocker.positions[6:]   ## Third row (bottom positions)
        ]
        

        for i, row in enumerate(positions_rows):
            if i == 0:  # First row
                text = '(' + ', '.join(row)
            elif i == len(positions_rows) - 1:  # Last row
                text = ', '.join(row) + ')'
            else:
                text = ', '.join(row)
            
            position_row_label = tk.Label(self.top, text=text)
            position_row_label.pack()



    def setup_password_section(self):
        #########################################################
        ## Password Section
        #########################################################
        
        
        password_section_label = tk.Label(
            self.top, 
            text="Password Management", 
            font=("Helvetica", self.title_font_size, "bold"))
        password_section_label.pack(pady=(10, 5))

        ## Current Password
        self.current_password_label = tk.Label(self.top, text="Current Password:")
        self.current_password_label.pack()
        self.current_password_entry = tk.Entry(self.top, show="*")
        self.current_password_entry.pack()

        ## New Password
        self.new_password_label = tk.Label(self.top, text="New Password:")
        self.new_password_label.pack()
        self.new_password_entry = tk.Entry(self.top, show="*")
        self.new_password_entry.pack()

        ## Confirm New Password
        self.confirm_password_label = tk.Label(self.top, text="Confirm New Password:")
        self.confirm_password_label.pack()
        self.confirm_password_entry = tk.Entry(self.top, show="*")
        self.confirm_password_entry.pack()

        ## Enable Encryption
        self.enable_encryption_var = tk.BooleanVar(value=False)
        self.enable_encryption_checkbox = tk.Checkbutton(self.top, text="Encrypt Password", variable=self.enable_encryption_var)
        self.enable_encryption_checkbox.pack()

    def on_close(self):
        self.top.destroy()
        self.master.deiconify()  
        self.master.focus_force()

    def update_display_option(self):
        if self.display_option_var.get() == 1:
            self.custom_msg_entry.config(state='disabled')
        else:
            self.custom_msg_entry.config(state='normal')

    def save_settings(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        enable_encryption = self.enable_encryption_var.get()

        if new_password and new_password == confirm_password:
            if self.smak_locker.validate_password(current_password):
                self.smak_locker.change_password(new_password, enable_encryption)
            else:
                tk.messagebox.showerror("Error", "Current password is incorrect.")
        elif new_password:
            tk.messagebox.showerror("Error", "New passwords do not match.")
        
        
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
                # 'password': self.smak_locker.password
            }
            self.smak_locker.update_settings(new_settings)
            self.on_close()
            
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input for position. Please enter two comma-separated numbers.")




if __name__ == "__main__":
    app = SmakLocker(show_password=True)
    # app.change_password()
    app.open_settings_dialog()
    systray = False
    if systray:
        app.run_systray()
    else:
        app.run()

