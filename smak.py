'''TODO
    Encrypted Passwords:
        - Experiment with an actual encrypted system
    
    EXE
        - Make this into an optional exe. 
    
    Startup with windows
        - Figure this out:
        - CMD & therefore maybe the startup command:
            python smak.py --systray
        - Make this optional but selected by defauult

    Pypi:
        - Upload to pypi
        - give the pypi and the github the picture, an icon. 
        

    '''


from print_tricks import pt

import json, ctypes, threading, sys, os, time
import tkinter as tk
from tkinter import font, messagebox, PhotoImage
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller

from pystray import MenuItem as item, Icon, Menu, MenuItem
from PIL import Image

## TODO: Consider moving this into Password management, and just import if encryption
## is checked. 
from cryptography.fernet import Fernet, InvalidToken
import base64

class SmakStopper:
    positions = [
            "top left", "top center", "top right",
            "center left", "center center", "center right",
            "bottom left", "bottom center", "bottom right"
        ]

    def __init__(self, master, password_manager, on_close_callback=None, show_password=False, custom_msg=None, position=None, size=12, alpha=0.1):
        # pt('init')
        self.master = master
        self.password_manager = password_manager
        self.on_close_callback = on_close_callback
        
        self.smak_window = tk.Toplevel(self.master)
        self.typed_keys = []
        self.listener = None
        
        self.load_settings()

    def load_settings(self, settings=None):
        if settings is None:
            settings = SettingsUtility.load_settings()
        
        self.settings = settings
        
        self.auto_lock_enabled = settings['auto_lock_enabled']
        self.auto_lock_time = settings['auto_lock_time']
        self.selected_image = settings['selected_image']
        self.show_nothing = settings['show_nothing']
        self.show_password = settings['show_password']
        self.show_custom_msg = settings['show_custom_msg']
        self.custom_msg = settings['custom_msg']
        self.position = settings['position']
        self.size = settings['size']
        self.alpha = settings['alpha']
        self.background_color = settings['background_color']
        self.enable_encryption = settings['enable_encryption']
        
        password = settings['password']
        if password is None or password == '':
            password = SettingsUtility.default_settings()['password']
        
        # Handle password decryption or direct application based on encryption setting
        if self.enable_encryption:
            encrypted_password = password
            try:
                decrypted_password = self.password_manager.decrypt_password(encrypted_password)
                self.password = list(decrypted_password) if decrypted_password else []
            except ValueError as e:
                print(f"Error decrypting password: {str(e)}")
                self.password = []  # Set to empty list if decryption fails
        else:
            self.password = list(password)  # Use the password directly if not encrypted

        self.setup_window()  

    def setup_window(self):

        
        self.smak_window.title('SMAK Stopper')
        self.smak_window.protocol("WM_DELETE_WINDOW", self.close)
        
        self.smak_window.configure(bg=self.background_color)
        
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
        
        if self.show_password or self.show_custom_msg:
            self.display_message()

    def display_message(self):
        self.custom_font = font.Font(family="Helvetica", size=self.size, weight="bold", underline=1)
        
        message = ''
        if self.show_password:
            password = ''.join(self.password)
            message = f'Type in "{password}" (without quotes) to unlock the screen'
        elif self.show_custom_msg:
            message = self.custom_msg  # Use the custom message set in settings

        selected_positions = self.settings.get('selected_positions', self.positions)
        if self.position:
            self.create_label(message, self.position)
        else:
            for position in selected_positions:
                x, y = self.calculate_position(position)
                self.create_label(message, (x, y))

    def calculate_position(self, position):
        vertical, horizontal = position.split()
        y = 0.1 if vertical == 'top' else 0.5 if vertical == 'center' else 0.9
        x = 0.1 if horizontal == 'left' else 0.5 if horizontal == 'center' else 0.9
        return x, y

    def create_label(self, message, position):
        if isinstance(position, str):
            position = self.calculate_position(position)
        x, y = position
        label = tk.Label(
            self.smak_window, text=message,
            fg='white', bg='black', font=self.custom_font
        )
        label.place(relx=x, rely=y, anchor='center')

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
        ## TODO: Remove this after testing
        self.on_press_development(key)
        
        ## keep this
        self.on_press_production(key)
        
    def on_press_development(self, key):
        if hasattr(key, 'char') and key.char == '1':
            ## TODO: Temporary destroy for testing. 
            self.close()    
            
    def on_press_production(self, key):
        if key == Key.esc and any(k in self.typed_keys for k in [Key.shift, Key.ctrl]):
            return

        if hasattr(key, 'char') and key.char:
            key_value = key.char
        else:
            key_value = key
        pt(key_value)

        self.typed_keys.append(key_value)
        # Ensure we only check the last 'n' characters where 'n' is the length of the encrypted password
        encrypted_password_length = len(''.join(self.password))  # Assuming self.password is the encrypted password

        if len(self.typed_keys) >= encrypted_password_length:
            self.typed_keys = self.typed_keys[-encrypted_password_length:]

            # Convert typed keys to a string for comparison
            typed_password = ''.join(self.typed_keys)

            if self.enable_encryption:
                # Decrypt the stored password for comparison only if the length matches
                if len(typed_password) == encrypted_password_length:
                    try:
                        decrypted_password = self.password_manager.decrypt_password(''.join(self.password))
                        if typed_password == decrypted_password:
                            self.close()
                    except ValueError as e:
                        print(f"Error decrypting password: {str(e)}")
            else:
                # Direct comparison if encryption is not enabled
                if typed_password == ''.join(self.password):
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
        if self.on_close_callback:
            self.on_close_callback() 







class PasswordManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.key_path = os.path.join(os.path.dirname(settings_path), 'secret.key')
        self.settings = SettingsUtility.load_settings()
        self.cipher = None  # Initialize cipher as None
        if self.settings.get('enable_encryption', False):
            self.initialize_cipher()

    def initialize_cipher(self):
        pt('initialize cipher')
        try:
            if os.path.exists(self.key_path):
                with open(self.key_path, 'rb') as key_file:
                    key_data = key_file.read()
                    self.key = base64.urlsafe_b64decode(key_data)
            else:
                # Key does not exist, generate a new one
                self.key = Fernet.generate_key()
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(base64.urlsafe_b64encode(self.key))
            self.cipher = Fernet(self.key)
        except Exception as e:
            print(f"Error initializing cipher: {e}")
            # Handle error (e.g., log, retry, alert user)

    def encrypt_password(self, password):
        pt('encrypting password')
        if not self.cipher:
            raise ValueError("Encryption is not enabled or cipher is not initialized.")
        encrypted_password = self.cipher.encrypt(password.encode())
        return encrypted_password.decode()

    def decrypt_password(self, encrypted_password):
        pt('decrypting password')
        if not self.cipher:
            raise ValueError("Encryption is not enabled or cipher is not initialized.")
        try:
            decrypted_password = self.cipher.decrypt(encrypted_password.encode())
            return decrypted_password.decode()
        except InvalidToken:
            print("Failed to decrypt: Invalid token or key.")
            return SettingsUtility.default_settings()['password']
        except Exception as e:
            print(f"Unexpected error during decryption: {e}")
            return SettingsUtility.default_settings()['password']

    def update_encryption_setting(self, enable_encryption):
        pt('update encryption setting')
        if enable_encryption and not self.cipher:
            self.initialize_cipher()
        elif not enable_encryption:
            self.cipher = None

    def load_or_generate_key(self):
        pt('loading or generating key')
        
        try:
            if os.path.exists(self.key_path):
                with open(self.key_path, 'rb') as key_file:
                    key_data = key_file.read()
                    self.key = base64.urlsafe_b64decode(key_data)
                    self.cipher = Fernet(self.key)
            else:
                self.key = Fernet.generate_key()
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(base64.urlsafe_b64encode(self.key))
                self.cipher = Fernet(self.key)
        except (ValueError, base64.binascii.Error) as e:
            print(f"Error decoding the Fernet key: {e}. Generating a new key.")
            self.key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(base64.urlsafe_b64encode(self.key))
            self.cipher = Fernet(self.key)

    def is_encrypted(self, data):
        ## TODO, I'm not sure I like this way of validating if it's encrypted.
        ## should I just use the variable? Or I can't because we are saving it now..
        
        try:
            # Attempt to decode the data from base64
            decoded_data = base64.urlsafe_b64decode(data)
            # Optionally, you could add more checks here to validate the decoded data
            return True
        except (ValueError, TypeError, base64.binascii.Error):
            return False
    
    def validate_password(self, current_password):
        pt('validating password')
        
        settings = SettingsUtility.load_settings()
        stored_encrypted_password = settings.get('password', None)
        if stored_encrypted_password:
            stored_password = self.decrypt_password(stored_encrypted_password)
            return stored_password == current_password
        return False


class SettingsUtility:
    auto_lock_time = 180
    
    @staticmethod
    def default_settings():
        return {
            'auto_lock_enabled': False,
            'auto_lock_time': SettingsUtility.auto_lock_time,
            'selected_image': 'baby_hand',
            'show_nothing': False,
            'show_password': False,
            'show_custom_msg': True,
            'custom_msg': 'Custom Message',
            'position': None,
            'size': 12,
            'alpha': 0.1,
            'background_color': 'black',
            'password': 'quit',
            'enable_encryption': False
        }

    @staticmethod
    def load_settings():
        settings_path = SettingsUtility.get_path()
        
        ## TODO DELETE THIS
        # settings = SettingsUtility.default_settings()

        #TDODO TEMP Temp commented out, for testing purposes
        try:
            with open(settings_path, 'r') as file:
                settings = json.load(file)
                for key, value in SettingsUtility.default_settings().items():
                    settings.setdefault(key, value)
        except FileNotFoundError:
            settings = SettingsUtility.default_settings()

        return settings

    @staticmethod
    def get_path():
        smak_folder_path = os.path.join(os.path.expanduser('~'), 'Documents', 'SMAK')
        if not os.path.exists(smak_folder_path):
            os.makedirs(smak_folder_path)
        settings_path = os.path.join(smak_folder_path, 'SMAK_settings.json')
        return settings_path


class SettingsDialog:
    def __init__(self, master, password_manager, manager=None, system_tray_app=None):
        self.master = master
        self.manager = manager
        self.system_tray_app = system_tray_app
        
        self.password_manager = password_manager
        
        self.settings_window = tk.Toplevel(self.master, )
        self.settings_window.title("SMAK Settings")
        self.label_section_font_size = 12
        
        ## This makes the window a tool window which removes the maximize and minimize buttons
        self.settings_window.attributes('-toolwindow', True)
        
        ## Set the window as modal and focus
        self.settings_window.transient(None)
        self.settings_window.grab_set()  ## Modal
        self.settings_window.focus_set()
        
        self.display_option_var = tk.IntVar(value=3)  ## Default to 'Show custom message'
        self.enable_encryption = tk.BooleanVar(value=False)
        
        self.load_settings()
        self.setup_window_contents()
        


    def close(self):
        ##  release the grab and destroy the window
        self.settings_window.grab_release()
        self.settings_window.destroy()
        if self.system_tray_app:
            self.system_tray_app.settings_win_inst = None

    def update_radio_display_option(self):
            """Enable or disable the custom message entry based on the selected radio button."""
            if self.display_option_var.get() == 3:
                self.custom_msg_entry.config(state='normal', bg='white')
            else:
                self.custom_msg_entry.config(state='disabled', bg='light grey')

    def get_screen_size(self):
        
        hdc = ctypes.windll.user32.GetDC(None)
        
        width = ctypes.windll.gdi32.GetDeviceCaps(hdc, 118)  ## 118 is HORZRES
        height = ctypes.windll.gdi32.GetDeviceCaps(hdc, 117)  ## 117 is VERTRES
        
        ctypes.windll.user32.ReleaseDC(None, hdc)
        
        return width, height

    def center_window(self):
        w, h = self.get_screen_size()
        
        size = tuple(int(_) for _ in self.settings_window.geometry().split('+')[0].split('x'))
        x = (w // 2) - (size[0] // 2)
        y = (h // 2) - (size[1] // 2)
        
        self.settings_window.geometry("+{}+{}".format(x, y))
        
        # pt(size, w,h,x,y)

    def setup_window_contents(self):
        
        ## Hide the window until all content loaded
        self.settings_window.withdraw()
        
        ## Set DPI awareness (No longer necessary, but will be more seamless/integrated)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        
        ## Setup contents
        self.setup_auto_lock_section()
        self.setup_image_selection()
        self.setup_window_appearance()
        self.setup_message_display_options()
        self.setup_password_section()
        self.setup_save_button()
        self.update_radio_display_option()

        self.settings_window.update()

        ## Bring back window into focus
        self.settings_window.deiconify()
        
        ## Center (NOTE: this has to happen after deiconify() or else it won't center properly)
        self.center_window()
        
        ## Tray
        self.manager.update_tray_icon()

    def setup_auto_lock_section(self):
        auto_lock_label = tk.Label(self.settings_window, text="Auto Lock Settings", font=("Helvetica", self.label_section_font_size, "bold"))
        auto_lock_label.pack(pady=(10, 5))

        self.auto_lock_var = tk.BooleanVar(value=self.settings.get('auto_lock_enabled', False))
        self.auto_lock_checkbox = tk.Checkbutton(self.settings_window, text="Enable Auto Lock", variable=self.auto_lock_var)
        self.auto_lock_checkbox.pack()

        self.auto_lock_time_label = tk.Label(self.settings_window, text="Auto Lock Time (minutes):")
        self.auto_lock_time_label.pack()
        self.auto_lock_time_entry = tk.Entry(self.settings_window)
        self.auto_lock_time_entry.insert(0, str(self.settings.get('auto_lock_time', 50)))
        self.auto_lock_time_entry.pack()

    def setup_image_selection(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        self.baby_hand_image = PhotoImage(file=os.path.join(dir_path, 'assets', 
            'SMAK_Hand_Icon.png'))
        self.cat_paw_image = PhotoImage(file=os.path.join(dir_path, 'assets', 
            'SMAK_Cat_Icon.png'))

        # Create a frame for image selection
        image_frame = tk.Frame(self.settings_window)
        image_frame.pack(pady=10)

        # Display images
        tk.Label(image_frame, image=self.baby_hand_image).grid(row=0, column=0)
        tk.Label(image_frame, image=self.cat_paw_image).grid(row=0, column=1)

        # Variables for radio buttons
        # self.selected_image_var = tk.StringVar(value='baby_hand')
        self.selected_image_var = tk.StringVar(value=self.settings.get('selected_image', 'baby_hand'))

        # Radio buttons for selecting the image
        tk.Radiobutton(image_frame, text="Baby Hand", variable=self.selected_image_var, value='baby_hand').grid(row=1, column=0)
        tk.Radiobutton(image_frame, text="Cat's Paw", variable=self.selected_image_var, value='cat_paw').grid(row=1, column=1)

    def setup_window_appearance(self):
        #########################################################
        ## Invisible Window Appearance
        #########################################################
        window_section_label = tk.Label(
            self.settings_window, text="Invisible Lockscreen Appearance", 
            font=("Helvetica", self.label_section_font_size, "bold"))
        window_section_label.pack(padx=(10,10), pady=(10, 5))
    
        ###################
        ## Alpha Transparency
        ###################
        if self.settings is None:
            return
        
        self.alpha_label = tk.Label(self.settings_window, text="Alpha (Transparency):").pack()
        self.alpha_entry = tk.Entry(self.settings_window)
        self.alpha_entry.insert(0, str(self.settings['alpha']))
        self.alpha_entry.pack()

        ###################
        ## Background Color
        ###################
        self.supported_colors = ['white', 'black', 'red', 'green', 'blue', 'cyan', 'yellow', 'magenta']
        
        self.bg_color_label = tk.Label(self.settings_window, text="Background Color:")
        self.bg_color_label.pack()
        
        self.bg_color_var = tk.StringVar()
        self.bg_color_var.set(self.settings['background_color'])
        
        self.bg_color_menu = tk.OptionMenu(self.settings_window, self.bg_color_var, *self.supported_colors)
        self.bg_color_menu.pack()

    def setup_message_display_options(self):
        #########################################################
        ## Message Display Options
        #########################################################
        window_section_label = tk.Label(
            self.settings_window, text="Display a Message", 
            font=("Helvetica", self.label_section_font_size, "bold"))
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
        
        self.position_checkboxes = {}
        positions_frame = tk.LabelFrame(self.settings_window, text="Message Locations", padx=5, pady=5)
        positions_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        for i, position in enumerate(SmakStopper.positions):
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(positions_frame, text=position, variable=var)
            chk.grid(row=i//3, column=i%3, sticky="w")
            self.position_checkboxes[position] = var

    def setup_password_section(self):
        #########################################################
        ## Password Section
        #########################################################
        
        password_section_label = tk.Label(
            self.settings_window, 
            text="Password Management", 
            font=("Helvetica", self.label_section_font_size, "bold"))
        password_section_label.pack(pady=(10, 5))

        password_frame = tk.Frame(self.settings_window)
        password_frame.pack(pady=5, fill=tk.X)

        ## Current Password
        self.current_password_label = tk.Label(password_frame, text="Current Password:")
        self.current_password_label.grid(row=0, column=0, sticky='e')
        self.current_password_entry = tk.Entry(password_frame, show="*")
        self.current_password_entry.grid(row=0, column=1, sticky='ew')
        self.toggle_current_password = tk.BooleanVar(value=False)
        self.current_password_checkbutton = tk.Checkbutton(
            password_frame, 
            text="Show", 
            variable=self.toggle_current_password,
            command=lambda: self.toggle_password_visibility(
                self.current_password_entry, self.toggle_current_password)
        )
        self.current_password_checkbutton.grid(row=0, column=2)

        ## New Password
        self.new_password_label = tk.Label(password_frame, text="New Password:")
        self.new_password_label.grid(row=1, column=0, sticky='e')
        self.new_password_entry = tk.Entry(password_frame, show="*")
        self.new_password_entry.grid(row=1, column=1, sticky='ew')
        self.toggle_new_password = tk.BooleanVar(value=False)
        self.new_password_checkbutton = tk.Checkbutton(
            password_frame, 
            text="Show", 
            variable=self.toggle_new_password,
            command=lambda: self.toggle_password_visibility(
                self.new_password_entry, self.toggle_new_password)
        )
        self.new_password_checkbutton.grid(row=1, column=2)

        ## Confirm New Password
        self.confirm_password_label = tk.Label(password_frame, text="Confirm New Password:")
        self.confirm_password_label.grid(row=2, column=0, sticky='e')
        self.confirm_password_entry = tk.Entry(password_frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, sticky='ew')
        self.toggle_confirm_password = tk.BooleanVar(value=False)
        self.confirm_password_checkbutton = tk.Checkbutton(
            password_frame, 
            text="Show", 
            variable=self.toggle_confirm_password,
            command=lambda: self.toggle_password_visibility(
                self.confirm_password_entry, self.toggle_confirm_password)
        )
        self.confirm_password_checkbutton.grid(row=2, column=2)

        ## Enable Encryption
        encryption_frame = tk.Frame(self.settings_window)
        encryption_frame.pack(fill=tk.X, pady=5)
        self.enable_encryption_checkbox = tk.Checkbutton(
            encryption_frame,
            text="Encrypt Password", 
            variable=self.enable_encryption  # Associate the BooleanVar with the Checkbutton
        )
        self.enable_encryption_checkbox.pack(side=tk.TOP, anchor='center')

    def toggle_password_visibility(self, entry_widget, toggle_var):
        if toggle_var.get():
            entry_widget.config(show="")
        else:
            entry_widget.config(show="*")

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
        
        ## Checkmark box
        self.enable_encryption.set(self.settings.get('enable_encryption', False))
        
        ## Radio Buttons
        if self.settings.get('show_nothing', False):
            self.display_option_var.set(1)
        elif self.settings.get('show_password', False):
            self.display_option_var.set(2)
        elif self.settings.get('show_custom_msg', False):
            self.display_option_var.set(3)

    def save_settings(self):


        auto_lock_enabled = self.auto_lock_var.get()
        auto_lock_time = self.process_auto_lock_time()

        selected_positions = [pos for pos, var in self.position_checkboxes.items() if var.get()]
        processed_password = self.process_password()
        encryption = self.enable_encryption.get()

        new_settings = {
            'auto_lock_enabled': auto_lock_enabled,
            'auto_lock_time': auto_lock_time,
            'selected_image': self.selected_image_var.get(),
            'show_nothing': self.display_option_var.get() == 1,
            'show_password': self.display_option_var.get() == 2,
            'show_custom_msg': self.display_option_var.get() == 3,
            'custom_msg': self.custom_msg_entry.get('1.0', 'end-1c'),
            'selected_positions': selected_positions,
            'size': int(self.size_entry.get()),
            'alpha': float(self.alpha_entry.get()),
            'background_color': self.bg_color_var.get(),
            'password': processed_password,
            'enable_encryption': encryption,  # Use the BooleanVar to get the state
        }

        settings_path = SettingsUtility.get_path()
        with open(settings_path, 'w') as file:
            json.dump(new_settings, file)

        ## start/stop listeners for auto_lock
        if self.manager:
            self.manager.load_auto_lock_settings()
            self.manager.reset_auto_lock_timer()
            self.manager.update_tray_icon()
            
            if auto_lock_enabled:
                self.manager.start_listeners()
            else:
                self.manager.stop_listeners()
            
                self.close()

    def process_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        enable_encryption = self.enable_encryption.get()

        if new_password:
            if new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match.")
                return None
            if not self.password_manager.validate_password(current_password):
                messagebox.showerror("Error", "Current password is incorrect.")
                return None
            # Encrypt the new password if encryption is enabled
            if enable_encryption:
                if not self.password_manager.cipher:
                    self.password_manager.initialize_cipher()
                return self.password_manager.encrypt_password(new_password)
            else:
                return new_password
        else:
            # No new password entered, handle existing password
            existing_password = self.settings.get('password', SettingsUtility.default_settings()['password'])
            if enable_encryption:
                if not self.password_manager.cipher:
                    self.password_manager.initialize_cipher()
                if not self.password_manager.is_encrypted(existing_password):
                    existing_password = self.password_manager.encrypt_password(existing_password)
                return existing_password
            else:
                # If encryption is not enabled, ensure the password is decrypted if it was encrypted
                if self.password_manager.is_encrypted(existing_password):
                    if not self.password_manager.cipher:
                        self.password_manager.initialize_cipher()
                    try:
                        existing_password = self.password_manager.decrypt_password(existing_password)
                    except Exception as e:
                        print(f"Failed to decrypt with error: {e}")
                        existing_password = SettingsUtility.default_settings()['password']
                        pt(existing_password)
                return existing_password

    def process_auto_lock_time(self):
        try:
            auto_lock_time = float(self.auto_lock_time_entry.get())
            ## Enforce a minimum auto-lock time of 0.1 minutes (6 seconds)
            if auto_lock_time < 0.1:
                auto_lock_time = 0.1
                tk.messagebox.showinfo("Notice", "Auto-lock time set to minimum of 0.1 minutes (6 seconds) to prevent accidental continous locking.")
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid auto lock time. Please enter a valid number.")
            return
        return auto_lock_time


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
        self.auto_lock_timer_thread = None
        self.auto_lock_time = SettingsUtility.auto_lock_time
        self.tray_icon = None
        self.icon_image_default = None
        self.icon_image_locked = None
        
        self.keyboard_listener = None
        self.mouse_listener = None
        self.auto_lock_timer = None
        
        self.password_manager = PasswordManager(SettingsUtility.get_path())

        
        self.load_auto_lock_settings()
        if self.auto_lock_enabled:
            self.start_listeners()

    def start_listeners(self):
        if not self.keyboard_listener:
            self.keyboard_listener = keyboard.Listener(on_press=self.reset_auto_lock_timer)
            self.keyboard_listener.start()
        if not self.mouse_listener:
            self.mouse_listener = mouse.Listener(on_move=self.reset_auto_lock_timer)
            self.mouse_listener.start()

    def stop_listeners(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.auto_lock_timer:
            self.auto_lock_timer.cancel()
            self.auto_lock_timer = None

    def load_auto_lock_settings(self):
        settings = SettingsUtility.load_settings()
        self.auto_lock_enabled = settings['auto_lock_enabled']
        self.auto_lock_time = float(settings['auto_lock_time']) * 60  ## Convert minutes to seconds

    def reset_auto_lock_timer(self, *args):
        # pt()
        if self.auto_lock_enabled:
            if self.auto_lock_timer:
                self.auto_lock_timer.cancel()
            self.auto_lock_timer = threading.Timer(self.auto_lock_time, self.auto_lock)
            self.auto_lock_timer.start()
        else:
            self.stop_listeners()

    def auto_lock(self):
        """ Trigger auto-lock by opening SmakStopper Window only if it's not already open."""
        if not self.window1 or not self.window1.smak_window.winfo_exists():
            self.root.after(0, self.toggle_window1)

    def update_tray_icon(self):
        if self.tray_icon:
            settings = SettingsUtility.load_settings()
            selected_image = settings.get('selected_image', 'baby_hand')
            dir_path = os.path.dirname(os.path.realpath(__file__))
            if selected_image == 'baby_hand':
                icon_image_default = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Hand_Icon.ico'))
                icon_image_locked = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Hand_Locked_Icon.ico'))
            elif selected_image == 'cat_paw':
                icon_image_default = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Cat_Icon.ico'))
                icon_image_locked = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Cat_Locked_Icon.ico'))
            
            self.tray_icon.icon = icon_image_default
            self.icon_image_default = icon_image_default
            self.icon_image_locked = icon_image_locked

    def toggle_window1(self):
        if not self.window1 or not self.window1.smak_window.winfo_exists():
            self.window1 = SmakStopper(
                master=self.root, 
                password_manager=self.password_manager,
                on_close_callback=self.on_window1_close)
            self.window1.run()
            if self.tray_icon:
                self.tray_icon.icon = self.icon_image_locked  ## Change icon to active
        else:
            self.window1.close()
            self.window1 = None
            if self.tray_icon:
                self.tray_icon.icon = self.icon_image_default  ## Change icon to default

    def on_window1_close(self):
        self.window1 = None
        if self.tray_icon:
            self.tray_icon.icon = self.icon_image_default  ## Change icon to default when window1 is closed

    def toggle_window2(self):
        if not self.window2 or not self.window2.settings_window.winfo_exists():
            self.window2 = SettingsDialog(
                master=self.root, 
                manager=self, 
                password_manager=self.password_manager)
        else:
            self.window2.settings_window.deiconify()  ## Restore the window if minimized
            self.window2.settings_window.lift()       ## Bring the window to the top
            self.window2.settings_window.focus_set()  ## Set focus to the window


class Win32PystrayIcon(Icon):
    WM_LBUTTONDBLCLK = 0x0203

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'on_double_click' in kwargs:
            self.on_double_click = kwargs['on_double_click']

    def _on_notify(self, wparam, lparam):
        super()._on_notify(wparam, lparam)
        if lparam == self.WM_LBUTTONDBLCLK:
            self.on_double_click(self, None)


def setup_tray_icon(window_manager):
    if sys.platform == 'win32':
        Icon = Win32PystrayIcon
        
    def quit_app(icon, window_manager):
        # pt.profile_memory()
        try:
            window_manager.stop_listeners()
            if window_manager.auto_lock_timer:
                window_manager.auto_lock_timer.cancel()
            
            icon.stop()
            sys.exit()
        except SystemExit:
            icon.stop()
            print("Application exited cleanly.")

    def on_double_click(icon, item):
        window_manager.toggle_window1()

    def update_icon():
        settings = SettingsUtility.load_settings()
        selected_image = settings.get('selected_image', 'baby_hand')
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if selected_image == 'baby_hand':
            icon_image_default = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Hand_Icon.ico'))
            icon_image_locked = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Hand_Locked_Icon.ico'))
        elif selected_image == 'cat_paw':
            icon_image_default = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Cat_Icon.ico'))
            icon_image_locked = Image.open(os.path.join(dir_path, 'assets', 'SMAK_Cat_Locked_Icon.ico'))
        
        icon.icon = icon_image_default
        window_manager.icon_image_default = icon_image_default
        window_manager.icon_image_locked = icon_image_locked

    menu = (
        MenuItem('__SMAK STOPPER__', lambda: None),
        Menu.SEPARATOR,
        MenuItem('Lock the Screen', lambda: window_manager.toggle_window1()),
        MenuItem('Settings', lambda: window_manager.toggle_window2()),
        MenuItem('Quit', lambda: quit_app(icon, window_manager))
    )
    icon = Icon(
        "SMAK Stopper", None, "SMAK Stopper", menu,
        on_double_click=on_double_click if sys.platform == "win32" else None
    )
    update_icon()  # Initial icon setup
    window_manager.tray_icon = icon  ## Store the icon in the WindowManager
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
    
    main_loop.run()





