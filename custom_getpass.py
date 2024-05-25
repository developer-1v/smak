import msvcrt
import random
import sys

def getpass(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = []
    while True:
        ch = msvcrt.getch()
        if ch == b'\r':  # Enter key is pressed
            print('')
            break
        elif ch == b'\x08':  # Handle backspace/delete key
            if len(password) > 0:
                # Erase the last character
                sys.stdout.write('\b \b' * random.randint(1, 5))
                sys.stdout.flush()
                password = password[:-1]
        else:
            # Append and display random number of asterisks
            password.append(ch.decode())
            sys.stdout.write('*' * random.randint(1, 5))
            sys.stdout.flush()
    return ''.join(password)

if __name__ == "__main__":
    password = custom_getpass()
