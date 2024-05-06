import tkinter as tk
from tkinter import simpledialog, font
from pynput import keyboard
from pynput.keyboard import Key, Controller

class SmackLocker:
    def __init__(self, display_code=False, custom_msg=None, position=None, size=12):
        self.root = tk.Tk()
        self.typed_keys = []
        self.unlock_sequence = ['q', 'u', 'i', 't']
        self.display_code = display_code
        self.custom_msg = custom_msg
        self.position = position
        self.size = size
        self.setup_window()
        self.start_keyboard_listener()

    def setup_window(self):
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True, '-topmost', True)
        self.root.attributes('-alpha', 0.1)
        self.root.overrideredirect(True)
        if self.display_code:
            self.display_unlock_sequence()

    def display_unlock_sequence(self, ):
        custom_font = font.Font(family="Helvetica", size=self.size, weight="bold", underline=1)
        
        if self.custom_msg is None:
            self.custom_msg=f'Type in "{"".join(self.unlock_sequence)}" (without quotes) to unlock the screen',
            
        if self.position:
            
            label = tk.Label(
                self.root, text=self.custom_msg,
                fg='white', bg='black', font=custom_font
            )
            x, y = self.position
            label.place(relx=x, rely=y, anchor='center')
        else:
            
            positions = [
                ('top', 'left'), ('top', 'center'), ('top', 'right'),
                ('center', 'left'), ('center', 'center'), ('center', 'right'),
                ('bottom', 'left'), ('bottom', 'center'), ('bottom', 'right')
            ]
            for vertical, horizontal in positions:
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

    def change_unlock_sequence(self):
        new_sequence = simpledialog.askstring("Input", "Enter new unlock sequence:", parent=self.root)
        if new_sequence:
            self.unlock_sequence = list(new_sequence)
            self.display_unlock_sequence()

    def on_press(self, key):
        if hasattr(key, 'char') and key.char:
            key_value = key.char
        else:
            key_value = key

        self.typed_keys.append(key_value)
        if len(self.typed_keys) > len(self.unlock_sequence):
            self.typed_keys = self.typed_keys[-len(self.unlock_sequence):]

        if self.typed_keys == self.unlock_sequence:
            self.root.destroy()

        if key == Key.esc and any(k in self.typed_keys for k in [Key.shift, Key.ctrl]):
            self.root.destroy()

    def start_keyboard_listener(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SmackLocker(display_code=True)
    app.change_unlock_sequence()
    app.run()