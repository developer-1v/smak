import tkinter as tk
from tkinter import simpledialog, font
from pynput import keyboard
from pynput.keyboard import Key, Controller

class SmakLocker:
    def __init__(self, display_code=False, custom_msg=None, position=None, size=12, alpha=0.1):
        self.root = tk.Tk()
        self.root.title('SMAK Locker')
        self.typed_keys = []
        self.password = ['q', 'u', 'i', 't']
        self.display_code = display_code
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
        self.setup_window()
        self.start_keyboard_listener()

    def setup_window(self):
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True, '-topmost', True)
        self.root.attributes('-alpha', self.alpha)
        self.root.overrideredirect(True)
        if self.display_code:
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
    
    def change_password(self):
        ## give focus on input box temporarily by removing topmost on tk window
        self.root.attributes('-topmost', False)
        
        new_sequence = simpledialog.askstring("Input", "Enter new unlock sequence:", parent=self.root)
        
        self.root.attributes('-topmost', True)
        
        if new_sequence:
            self.password = list(new_sequence)
            self.display_password()
        
        self.root.focus_force() 

    def open_settings_dialog(self):
        initial_settings = {
            'display_code': self.display_code,
            'custom_msg': self.custom_msg,
            'position': self.position,
            'size': self.size,
            'alpha': self.alpha
        }
        settings_dialog = SettingsDialog(self, self.root, initial_settings)
        
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

    def start_keyboard_listener(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

    def run(self):
        self.root.mainloop()

class SettingsDialog:
    def __init__(self, smak_locker,master, initial_settings):
        self.smak_locker = smak_locker
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("SMAK Settings")
        self.settings = initial_settings

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

        # Make the settings window modal
        self.top.transient(master)
        self.top.grab_set()
        self.top.focus_set()
        self.top.attributes('-topmost', True)

        ###################
        ## Display Password
        ###################
        self.display_code_var = tk.BooleanVar(value=self.settings['display_code'])
        self.display_code_checkbox = tk.Checkbutton(self.top, text="Display Unlock Code", variable=self.display_code_var)
        self.display_code_checkbox.pack()

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
        self.settings['display_code'] = self.display_code_var.get()
        self.settings['custom_msg'] = self.custom_msg_entry.get()
        position_text = self.position_entry.get()
        if position_text:
            x, y = map(float, position_text.split(','))
            self.settings['position'] = (x, y)
        self.settings['size'] = int(self.size_entry.get())
        self.settings['alpha'] = float(self.alpha_entry.get())
        self.on_close()

    def on_close(self):
        self.top.grab_release()
        self.top.destroy()
        self.master.focus_set()
        self.master.attributes('-topmost', True)

if __name__ == "__main__":
    app = SmakLocker(display_code=True)
    # app.change_password()
    app.open_settings_dialog()
    app.run()

