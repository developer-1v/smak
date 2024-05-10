'''TODO
    Encrypted Passwords:
        - Experiment with an actual encrypted system
        

    Double Click to launch:
        - like toddler keys
    
    
    Bugs:
        - custom message not showing up again (might have something to do with positions)
        - custom position will fail, at least if using text.
        - quit button not properly quitting
        - The default option is always set to custom message radio button, even after the 
        settings loads. They should be dynamic and switch to whatever the settings had. 

        - Several of the settings that I have, if they don't retrieve a variable, are
        supposed to default to something. But I am manually setting this default at least
        twice: Once in smak stopper, and at least one more time in settings dialog. The 
        solution is have both of these refer to a variable in the settings utility
        class. 
        - There is a conflict between the words "show_message", which used to be 
        "show_password" and the new "show_password". I think I need to call show_message
        somethign completely random for a while while I figure out which is which. 
            - Ands then show_message should be _show_message or just deleted completely. 
            - Then in smak stopper, we don't even need to check for any of these, we just
            load whatever the message is (whether it's nothing which is '' or default
            password version, or a custom message.)

    
    EXE
        - Make this into an optional exe. 
    
    Startup with windows
        - Figure this out:
        - CMD & therefore maybe the startup command:
            python smak.py --systray
    
    Real Icon:
        - Maybe a babies hand with a rattle, smashing the keyboard. 
        - This is from a larger image where maybe a cat's paw is also on the keyboard?
        
    Swap Icons on lock
    
    Readme:
        - Make it a humorous readme. Maybe ask for help with this? 
    
    Pypi:
        - Upload to pypi
        - give the pypi and the github the picture, an icon. 
    
    '''
from print_tricks import pt

import json, ctypes, threading, sys, os
import tkinter as tk
from tkinter import font
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller

from pystray import MenuItem as item, Icon, Menu
from PIL import Image

class SmakStopper:
    positions = [
            "top left", "top center", "top right",
            "center left", "center center", "center right",
            "bottom left", "bottom center", "bottom right"
        ]

    def __init__(self, master, show_message=False, custom_msg=None, position=None, size=12, alpha=0.1):
        # pt('init')
        self.master = master
        self.smak_window = tk.Toplevel(self.master)
        
        self.typed_keys = []
        self.password = "quit"
        self.show_custom_msg = True
        self.show_message = show_message
        self.custom_msg = custom_msg
        self.position = position

        self.size = size
        self.alpha = alpha
        self.labels = []
        self.listener = None
        
        
        self.load_settings()

    def load_settings(self):
        settings = SettingsUtility.load_settings()
        self.auto_lock_enabled = settings.get('auto_lock_enabled', False)
        self.auto_lock_time = settings.get('auto_lock_time', 3600)
        self.message_type = settings.get('message_type', 'custom')
        self.show_nothing = settings.get('show_nothing', False)
        self.show_password = settings.get('show_password', True)
        self.show_message = settings.get('show_message', False)
        self.show_custom_msg = settings.get('show_custom_msg', True)
        self.custom_msg = settings.get('custom_msg', None)
        self.position = settings.get('position', None)
        self.size = settings.get('size', 12)
        self.alpha = settings.get('alpha', 0.1)
        self.password = list(settings.get('password', self.password))

    def update_settings(self, new_settings):
        self.auto_lock_enabled = new_settings['auto_lock_enabled']
        self.auto_lock_time = new_settings['auto_lock_time']
        self.message_type = new_settings['message_type']
        self.show_nothing = new_settings['show_nothing']
        self.show_password = new_settings['show_password']
        self.show_message = new_settings['show_message']
        self.show_custom_msg = new_settings['show_custom_msg']
        self.custom_msg = new_settings['custom_msg']
        self.position = new_settings['position']
        self.size = new_settings['size']
        self.alpha = new_settings['alpha']
        self.password = new_settings['password']
        
        self.setup_window()

    def setup_window(self):
        # if not self.smak_window:
        #     return
        
        self.smak_window.title('SMAK Stopper')
        self.smak_window.protocol("WM_DELETE_WINDOW", self.close)
        
        self.smak_window.configure(bg='black')
        
        ################################
        ##  TODO: I don't remember what these override's are for... and why wasn't fullscreen working
        ## with dpi awareness? Possibly test on other PC's with the 'zoomed' and 'fullscreen'. 
        ## Temporarily unset override-redirect to change fullscreen attribute
        self.smak_window.overrideredirect(False)
        self.smak_window.state('zoomed')
        ## self.smak_window.attributes('-fullscreen', True)
        self.smak_window.attributes('-topmost', True)
        ## Reapply override-redirect if needed
        self.smak_window.overrideredirect(True)
        ##############################################################
        
        self.smak_window.attributes('-alpha', self.alpha)
        if self.show_message:
            self.display_message()

    def display_message(self):
        # if not self.smak_window:
        #     return
        
        
        self.custom_font = font.Font(family="Helvetica", size=self.size, weight="bold", underline=1)
        
        if self.message_type == 'password':
            password = ''.join(self.password)
            self.custom_msg = f'Type in "{password}" (without quotes) to unlock the screen'
        elif self.message_type == 'custom':
            self.custom_msg = self.custom_msg
        else:
            self.custom_msg = ''
        
        if self.position:
            label = tk.Label(
                self.smak_window, text=self.custom_msg,
                fg='white', bg='black', font=self.custom_font
            )
            x, y = self.position
            label.place(relx=x, rely=y, anchor='center')
            self.labels.append(label)
        else:
            for position in self.positions:
                vertical, horizontal = position.split()
                label = tk.Label(
                    self.smak_window, text=self.custom_msg,
                    fg='white', bg='black', font=self.custom_font
                )
                if vertical == 'top':
                    y = 0.1
                elif vertical == 'center':
                    y = 0.5
                else:  ## bottom
                    y = 0.9
                
                if horizontal == 'left':
                    x = 0.1
                elif horizontal == 'center':
                    x = 0.5
                else:  ## right
                    x = 0.9
                
                label.place(relx=x, rely=y, anchor='center')
                self.labels.append(label)

    def start_keyboard_listener(self):
        ## Suppress keys
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
        self.start_keyboard_listener()
        self.setup_window()
    
    def close(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        if self.smak_window and hasattr(self.smak_window, 'tk') and self.smak_window.winfo_exists():
            self.smak_window.destroy()


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

    def validate_password(self, current_password):
        settings = self.load_settings()
        stored_password = settings.get('password', 'quit')
        return stored_password == current_password

    def encrypt_password(self, password):
        ## TODO: Implement encryption
        return password 


class SettingsUtility:
    
    @staticmethod
    def load_settings():
        settings_path = SettingsUtility.get_path()
        default_settings = {
            'auto_lock_enabled': False,
            'auto_lock_time': 3600,
            'message_type': 'custom',
            'show_nothing': False,
            'show_message': False,
            'show_custom_msg': True,
            'custom_msg': 'Display a Password Hint, or display password, or show nothing',
            'position': None,
            'size': 12,
            'alpha': 0.1,
            'password': 'quit'
        }
        try:
            with open(settings_path, 'r') as file:
                settings = json.load(file)
                # Ensure all default settings are present
                for key, value in default_settings.items():
                    settings.setdefault(key, value)
        except FileNotFoundError:
            settings = default_settings
            

        return settings

    @staticmethod
    def get_path():
        smak_folder_path = os.path.join(os.path.expanduser('~'), 'Documents', 'SMAK')
        if not os.path.exists(smak_folder_path):
            os.makedirs(smak_folder_path)
        settings_path = os.path.join(smak_folder_path, 'SMAK_settings.json')
        return settings_path


class SettingsDialog:
    def __init__(self, master, system_tray_app=None):
        self.master = master
        self.system_tray_app = system_tray_app
        
        self.password_manager = PasswordManager(SettingsUtility.get_path())

        self.settings_window = tk.Toplevel(self.master)
        self.settings_window.title("SMAK Settings")

        self.display_option_var = tk.IntVar(value=3)  # Default to 'Show custom message'

        self.title_font_size = 12
        
        ## Set the window as modal and focus
        self.settings_window.transient(None)
        self.settings_window.grab_set()  ## Modal
        self.settings_window.focus_set()
        self.settings_window.attributes('-topmost', True)
        
        self.load_settings()
        self.setup_window_contents()
        
        ## Set DPI awareness (No longer necessary, but will be more seamless/integrated)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    
    def close(self):
        ##  release the grab and destroy the window
        self.settings_window.grab_release()
        self.settings_window.destroy()
        if self.system_tray_app:
            self.system_tray_app.settings_win_inst = None
    

    
    def get_screen_size(self):
        
        hdc = ctypes.windll.user32.GetDC(None)
        
        width = ctypes.windll.gdi32.GetDeviceCaps(hdc, 118)  ## 118 is HORZRES
        height = ctypes.windll.gdi32.GetDeviceCaps(hdc, 117)  ## 117 is VERTRES
        
        ctypes.windll.user32.ReleaseDC(None, hdc)
        
        return width, height
    
    def center_window(self):
        # pt("center_window")
        w, h = self.get_screen_size()
        size = tuple(int(_) for _ in self.settings_window.geometry().split('+')[0].split('x'))
        x = (w // 2) - (size[0] // 2)
        y = (h // 2) - (size[1] // 2)
        self.settings_window.geometry("+{}+{}".format(x, y))
        # pt(w,h,x,y)

    def update_radio_display_option(self):
            """Enable or disable the custom message entry based on the selected radio button."""
            if self.display_option_var.get() == 3:
                self.custom_msg_entry.config(state='normal', bg='white')
            else:
                self.custom_msg_entry.config(state='disabled', bg='light grey')

    def setup_window_contents(self):
        self.setup_window_appearance()
        self.setup_message_display_options()
        self.setup_password_section()
        self.setup_auto_lock_section()
        self.setup_save_button()
        self.update_radio_display_option()
        self.settings_window.update()
        self.center_window()

    def setup_auto_lock_section(self):
        auto_lock_label = tk.Label(self.settings_window, text="Auto Lock Settings", font=("Helvetica", self.title_font_size, "bold"))
        auto_lock_label.pack(pady=(10, 5))

        self.auto_lock_var = tk.BooleanVar(value=self.settings.get('auto_lock_enabled', False))
        self.auto_lock_checkbox = tk.Checkbutton(self.settings_window, text="Enable Auto Lock", variable=self.auto_lock_var)
        self.auto_lock_checkbox.pack()

        self.auto_lock_time_label = tk.Label(self.settings_window, text="Auto Lock Time (minutes):")
        self.auto_lock_time_label.pack()
        self.auto_lock_time_entry = tk.Entry(self.settings_window)
        self.auto_lock_time_entry.insert(0, str(self.settings.get('auto_lock_time', 50)))
        self.auto_lock_time_entry.pack()
        
    def setup_window_appearance(self):
        #########################################################
        ## Invisible Window Appearance
        #########################################################
        window_section_label = tk.Label(
            self.settings_window, text="Invisible Lockscreen Appearance", 
            font=("Helvetica", self.title_font_size, "bold"))
        window_section_label.pack(pady=(10, 5))
    
        ###################
        ## Alpha Transparency
        ###################
        if self.settings is None:
            return
        
        self.alpha_label = tk.Label(self.settings_window, text="Alpha (Transparency):").pack()
        self.alpha_entry = tk.Entry(self.settings_window)
        self.alpha_entry.insert(0, str(self.settings['alpha']))
        self.alpha_entry.pack()

    def setup_message_display_options(self):
        #########################################################
        ## Message Display Options
        #########################################################
        window_section_label = tk.Label(
            self.settings_window, text="Display a Message", 
            font=("Helvetica", self.title_font_size, "bold"))
        window_section_label.pack(pady=(10, 5))

        ###################
        ## Show password, custom message, or nothing Radio Buttons
        ###################        

        ## Frame for radio buttons
        radio_frame = tk.Frame(self.settings_window)
        radio_frame.pack()

        self.radio_nothing = tk.Radiobutton(
            radio_frame, text="Show Nothing", variable=self.display_option_var, value=1,
            command=self.update_radio_display_option)
        self.radio_nothing.pack(side=tk.TOP, anchor='w')

        self.radio_password = tk.Radiobutton(
            radio_frame, text="Show password on lock screen", variable=self.display_option_var, value=2,
            command=self.update_radio_display_option)
        self.radio_password.pack(side=tk.TOP, anchor='w')

        self.radio_custom_msg = tk.Radiobutton(
            radio_frame, text="Show custom message:", variable=self.display_option_var, value=3,
            command=self.update_radio_display_option)
        self.radio_custom_msg.pack(side=tk.TOP, anchor='w')

        ## Custom Message Entry (only enabled if custom message option is selected)
        custom_msg = self.settings['custom_msg'] if self.settings['custom_msg'] is not None else ''
        self.custom_msg_entry = tk.Text(self.settings_window, height=2, wrap=tk.WORD, width=22)
        self.custom_msg_entry.insert(tk.END, custom_msg)
        self.custom_msg_entry.pack(fill=tk.Y, expand=True)





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
            self.position_entry.insert(0, self.settings['position'])
        self.position_entry.pack()
        pt(self.position_entry)

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
            if i == 0:  ## First row
                text = '(' + ', '.join(row)
            elif i == len(positions_rows) - 1:  ## Last row
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

    def setup_save_button(self):
        self.save_button = tk.Button(
            self.settings_window, 
            text="Save Settings", 
            command=self.save_settings,
            width=16, height=3
            )
        self.save_button.pack(pady=(25, 20))
    def change_password(self, new_password, enable_encryption=False):
        if enable_encryption:
            new_password = self.password_manager.encrypt_password(new_password)
        return new_password

    def load_settings(self):
        self.settings = SettingsUtility.load_settings()
        if self.settings is None:
            self.settings = {
                'message_type': 'custom',
                'show_nothing': False,
                'show_message': False,
                'show_custom_msg': True,
                'custom_msg': 'Display a Password Hint, or display password, or show nothing',
                'position': None,
                'size': 12,
                'alpha': 0.1,
                'password': 'quit',
                'enable_encryption': False,
                'auto_lock_enabled': False,
                'auto_lock_time': 3600
            }
            
        if self.settings.get('show_nothing', False):
            self.display_option_var.set(1)
        elif self.settings.get('show_message', False):
            self.display_option_var.set(2)
        elif self.settings.get('show_custom_msg', False):  # Default to True if none are set
            self.display_option_var.set(3)

    def save_settings(self):

        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        enable_encryption = self.enable_encryption_var.get()
        password = self.settings.get('password', 'quit')

        if new_password and new_password == confirm_password:
            if self.password_manager.validate_password(current_password):
                password = self.change_password(new_password, enable_encryption)
            else:
                tk.messagebox.showerror("Error", "Current password is incorrect.")
        elif new_password:
            tk.messagebox.showerror("Error", "New passwords do not match.")

        message_type = 'none'  # Default to 'none'
        if self.display_option_var.get() == 2:
            message_type = 'password'
        elif self.display_option_var.get() == 3:
            message_type = 'custom'

        auto_lock_enabled = self.auto_lock_var.get()
                
        try:
            auto_lock_time = float(self.auto_lock_time_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid auto lock time. Please enter a valid number.")
            return
        
        position = None
        try:
            position_input = self.position_entry.get().strip().replace(',', ' ')
            pt(position_input)
            if position_input and position_input != '':
                valid_positions = set(SmakStopper.positions)

                if position_input.lower() in valid_positions:
                    position = position_input

        except ValueError as e:
            tk.messagebox.showerror("Error", str(e) + " Please enter a valid position from the list: " + ', '.join(SmakStopper.positions))

        new_settings = {
            'auto_lock_enabled': auto_lock_enabled,
            'auto_lock_time': auto_lock_time,
            'message_type': message_type,
            'show_nothing': self.display_option_var.get() == 1,
            'show_message': self.display_option_var.get() == 2,
            'show_custom_msg': self.display_option_var.get() == 3,
            'custom_msg': self.custom_msg_entry.get('1.0', 'end-1c'),
            'position': position,
            'size': int(self.size_entry.get()),
            'alpha': float(self.alpha_entry.get()),
            'password': password,
            'enable_encryption': enable_encryption,
        }
        
        settings_path = SettingsUtility.get_path()
        with open(settings_path, 'w') as file:
            json.dump(new_settings, file)

            self.close()


class MainTKLoop:
    def __init__(self, root) -> None:
        self.root = root
        self.root.withdraw()

    def run(self):
        self.root.mainloop()  

class WindowManager:
    def __init__(self, root):
        self.root = root
        self.window1 = None
        self.window2 = None
        self.auto_lock_timer = None
        self.inactivity_delay = 50
        
        self.load_auto_lock_settings()

        self.start_listeners()

    def start_listeners(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.reset_auto_lock_timer)
        self.mouse_listener = mouse.Listener(on_move=self.reset_auto_lock_timer)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def load_auto_lock_settings(self):
        settings = SettingsUtility.load_settings()
        self.auto_lock_enabled = settings['auto_lock_enabled']
        # Parse auto_lock_time as float to allow decimal values
        self.inactivity_delay = float(settings['auto_lock_time']) * 60  # Convert minutes to seconds

    def reset_auto_lock_timer(self, *args):
        if self.auto_lock_enabled:
            if self.auto_lock_timer is not None:
                self.auto_lock_timer.cancel()
            self.auto_lock_timer = threading.Timer(self.inactivity_delay, self.auto_lock)
            self.auto_lock_timer.start()
            
    def reset_auto_lock_timer(self, *args):
        """ Reset the auto-lock timer whenever there is keyboard or mouse activity. """
        if self.auto_lock_timer is not None:
            self.auto_lock_timer.cancel()
        self.auto_lock_timer = threading.Timer(self.inactivity_delay, self.auto_lock)
        self.auto_lock_timer.start()

    def toggle_window1(self):
        if not self.window1 or not self.window1.smak_window.winfo_exists():
            self.window1 = SmakStopper(master=self.root)
            self.window1.run()
        else:
            self.window1.close()
            self.window1 = None

    def toggle_window2(self):
        if not self.window2 or not self.window2.settings_window.winfo_exists():
            self.window2 = SettingsDialog(master=self.root)
        else:
            self.window2.close()
            self.window2 = None

    def auto_lock(self):
        """ Trigger auto-lock by opening SmakStopper Window only if it's not already open."""
        if not self.window1 or not self.window1.smak_window.winfo_exists():
            self.root.after(0, self.toggle_window1)
        
def setup_tray_icon(window_manager):
    def quit_app(icon):
        icon.stop()
        sys.exit()
        
    
    icon_image = Image.new('RGB', (64, 64), color = 'red')
    menu = (
        item('__SMAK STOPPER__', lambda: None),
        Menu.SEPARATOR,
        item('Lock the Screen', lambda: window_manager.toggle_window1()),
        item('Settings', lambda: window_manager.toggle_window2()),
        item('Quit', lambda: quit_app(icon))
    )
    icon = Icon("Test Tray", icon_image, "Test Tray", menu)
    icon.run()

if __name__ == "__main__":
    root = tk.Tk()
    main_loop = MainTKLoop(root)
    manager = WindowManager(root)
    
    systray = True
    if systray:
        icon_thread = threading.Thread(
            target=setup_tray_icon,
            args=(manager,),
            daemon=True)
        icon_thread.start()
    else:
        app = SmakStopper(root, show_message=True)
        app.run()
        
    main_loop.run()




