import sys
import random
import secrets
import msvcrt

def getpass(
    prompt="Password: ", 
    character='*', 
    display_nothing=False, 
    use_random_characters=False, 
    characters='abcdefghijklmnopqrstuvwxyz'
    ):
    
    """
    Function to securely get a password from the user, using the GetPass class.

    Parameters:
    - prompt (str): Message displayed for input. Default is "Password: ".
    - character (str): Character displayed per keystroke. Default is '*'.
    - display_nothing (bool): If True, hides characters during input (most secure). Default is False.
    - use_random_characters (bool): If True, displays random characters. Default is False.
    - characters (str): Characters used if `use_random_characters` is True. Default is lowercase alphabets.

    Returns:
    - str: The securely inputted password.
    """
    password_instance = GetPass(prompt, character, display_nothing, use_random_characters, characters)
    return password_instance.password

class GetPass:
    """
    This class provides a secure method for password input with
    customization and security features.

    Features:
    - Customizable prompt message.
    - Displays asterisks (*), nothing (blanks, most secure), or any
        other custom character(s) when the user types in the password.
    - Provides password feedback so the user knows they are typing.
    - Option to display nothing when typing for increased security.
    - Uses random characters from a set to add confusion against
        shoulder-surfing.
    - Randomly deletes displayed characters as the user types,
        obscuring password length.

    Security Measures:
    - Passwords are masked or replaced with random number of
        characters, not shown in plain text.
    - Obscures actual password length by randomly deleting displayed
        characters, and randomizing the number of characters displayed.
    - Utilizes `msvcrt` module on Windows to handle input without
        echoing characters.
    - Randomizes maximum password display length to prevent deducing
        password length.

    Parameters:
    - prompt (str): Message displayed for input. Default is "Password: ".
    - character (str): Character displayed per keystroke. Default is '*'.
    - display_nothing (bool): If True, hides characters during input
        (most secure). Default is False.
    - use_random_characters (bool): If True, displays random characters.
        Default is False.
    - characters (str): Characters used if `use_random_characters` is
        True. Default is lowercase alphabets.

    Usage:
    Instantiate GetPass with desired settings. The password is securely
    prompted and stored upon creation.
    """
    
    
    def __init__(self, 
            prompt="Password: ", 
            character='*', 
            display_nothing=False, 
            use_random_characters=False, 
            characters='abcdefghijklmnopqrstuvwxyz'
            ):
        
        self.prompt = prompt
        self.character = '' if display_nothing else character
        self.use_random_characters = use_random_characters
        self.characters = characters
        self.min_length = 1
        self.max_length = secrets.randbelow(35) + 28
        self.password = self.get_pass()
        

    # def __str__(self):
    #     return self.password  ## Return the password when the object is printed


    def get_pass(self):
        print(self.prompt, end='', flush=True)
        password = []
        if sys.platform.startswith('win'):
            password = self.getpass_windows(password)
        ## TODO: implement unix version
        # else:
        #     password = self.getpass_unix(password)
        return ''.join(password)

    def getpass_windows(self, password):
        displayed_count = 0  # Initialize displayed character count
        enter_key = b'\r'
        backspace_key = b'\x08'
        while True:
            ch = msvcrt.getch()
            if ch == enter_key:
                print('')
                break
            elif ch == backspace_key:
                if displayed_count > 0:
                    delete_count = secrets.randbelow(displayed_count) + 1
                    sys.stdout.write('\b \b' * delete_count)
                    sys.stdout.flush()
                    password = password[:-delete_count]
                    displayed_count -= delete_count
            else:
                password, displayed_count = self.append_display_char(password, ch.decode(), displayed_count)
        return password

    def append_display_char(self, password, ch, displayed_count):
        password.append(ch)
        delete_count = 0
        if displayed_count > self.min_length:
            delete_count = random.randint(self.min_length, displayed_count)
            sys.stdout.write('\b \b' * delete_count)
            displayed_count -= delete_count
        display_count = random.randint(self.min_length, self.max_length)
        while display_count == delete_count:
            display_count = random.randint(self.min_length, self.max_length)
        if self.use_random_characters:
            display_chars = ''.join(random.choice(self.characters) for _ in range(display_count))
            sys.stdout.write(display_chars)
        else:
            sys.stdout.write(self.character * display_count)
        displayed_count += display_count
        sys.stdout.flush()
        return password, displayed_count

if __name__ == "__main__":
    password = getpass(
        character='*', 
        # display_nothing=False,
        use_random_characters=True,
        characters=')(*&^%$#@!+=-0987654321;":][}{\|/?.>,<}]'
        )
    print(password)


# import sys
# import random
# import secrets

# def getpass(
#         prompt="Password: ", 
#         character='*', 
#         display_nothing=False, 
#         use_random_characters=False, 
#         characters='abcdefghijklmnopqrstuvwxyz'
#         ):
    
#     print(prompt, end='', flush=True)
#     character = '' if display_nothing else character
#     password = []
#     min_length = 1
#     max_length = secrets.randbelow(9) + 7  ## randbelow(9) gives a number from 0 to 8, adding 7 shifts it to 7 to 15
    

#     if sys.platform.startswith('win'):
#         password = getpass_windows(password, min_length, max_length, use_random_characters, characters, character)
#     ## TODO: implement unix version
#     # else:
#     #     password = getpass_unix(password, min_length, max_length, use_random_characters, characters, character)

#     return ''.join(password)

# def getpass_windows(password, min_length, max_length, use_random_characters, characters, character):
#     import msvcrt
#     displayed_count = 0  # Initialize displayed character count
#     enter_key = b'\r'
#     backspace_key = b'\x08'
#     while True:
#         ch = msvcrt.getch()
#         if ch == enter_key:
#             print('')
#             break
#         elif ch == backspace_key:
#             if displayed_count > 0:
#                 delete_count = secrets.randbelow(displayed_count) + 1
#                 sys.stdout.write('\b \b' * delete_count)
#                 sys.stdout.flush()
#                 password = password[:-delete_count]
#                 displayed_count -= delete_count
#         else:
#             password, displayed_count = append_display_char(password, ch.decode(), min_length, max_length, use_random_characters, characters, character, displayed_count)
#     return password

# def append_display_char(password, ch, min_length, max_length, use_random_characters, characters, character, displayed_count):
#     password.append(ch)
    
#     delete_count = 0

#     ## Randomly decide the number of characters to delete from display
#     if displayed_count > min_length:
#         delete_count = random.randint(min_length, displayed_count)
#         # Clear the deleted characters from the display
#         sys.stdout.write('\b \b' * delete_count)
#         displayed_count -= delete_count
    
#     # Determine the number of characters to display, ensuring it's not equal to delete_count
#     display_count = random.randint(min_length, max_length)
#     while display_count == delete_count:
#         display_count = random.randint(min_length, max_length)
    
#     if use_random_characters:
#         display_chars = ''.join(random.choice(characters) for _ in range(display_count))
#         sys.stdout.write(display_chars)
#     else:
#         display_char = character
#         sys.stdout.write(display_char * display_count)
    
#     # Update the displayed count
#     displayed_count += display_count
    
#     sys.stdout.flush()
#     return password, displayed_count

# if __name__ == "__main__":
#     password = getpass(
#         character='*', ## pass '' to display nothing
#         # display_nothing=True,
#         use_random_characters=False
#     )
#     print(password)



'''
def getpass_unix(password, min_length, max_length, use_random_characters, characters, character):
    import tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    try:
        while True:
            ch = sys.stdin.read(1)
            if ch in ('\r', '\n'):
                print('')
                break
            elif ch == '\x08' or ch == '\x7f':
                if len(password) > 0:
                    sys.stdout.write('\b \b' * random.randint(min_length, max_length))
                    sys.stdout.flush()
                    password = password[:-1]
            else:
                append_display_char(password, ch, min_length, max_length, use_random_characters, characters, character)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password
    
    '''