import os

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode

from custom_getpass import getpass

def derive_key(password: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """ Derive a cryptographic key from a password with configurable iterations """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return urlsafe_b64encode(key)

def secure_delete(file_path: str, passes: int = 3):
    """ Overwrite the file with random data and then delete it """
    with open(file_path, "r+b") as file:
        length = os.path.getsize(file_path)
        for _ in range(passes):
            file.seek(0)
            file.write(os.urandom(length))
    os.remove(file_path)

def update_salt(salt: bytes):
    """ Securely update the salt file """
    if os.path.exists("salt.key"):
        secure_delete("salt.key")
    save_salt(salt)

def update_encrypted_data(encrypted_data: bytes):
    """ Securely update the encrypted data file """
    if os.path.exists("credentials.txt"):
        secure_delete("credentials.txt")
    save_encrypted_data(encrypted_data)

def validate_password(password: str) -> bool:
    min_pass_length = 1
    require_letters = False
    require_digits = False
    require_capitals = False
    require_symbols = False
    """ Validate the password to ensure it meets the criteria """
    if len(password) < min_pass_length:
        print(f"Password must be at least {min_pass_length} character(s) long.")
        return False
    if require_digits and not any(char.isdigit() for char in password):
        print("Password must contain at least one digit.")
        return False
    if require_letters and not any(char.isalpha() for char in password):
        print("Password must contain at least one letter.")
        return False
    if require_capitals and not any(char.isupper() for char in password):
        print("Password must contain at least one uppercase letter.")
        return False
    if require_symbols and not any(not char.isalnum() for char in password):
        print("Password must contain at least one symbol.")
        return False
    return True

def setup_password():
    """ Setup password and save salt and encrypted data """
    password = getpass("Set up password: ")
    if not validate_password(password):
        return
    salt = os.urandom(16)
    update_salt(salt)
    iterations = 150_000
    key = derive_key(password, salt, iterations)
    data_to_encrypt = b"Example sensitive data"
    encrypted_data = encrypt_data(data_to_encrypt, key)
    update_encrypted_data(encrypted_data)
    print("Password setup complete and data encrypted.")

def unlock_password():
    """ Attempt to unlock with a password """
    try:
        salt = load_salt()
    except FileNotFoundError:
        print("Salt file not found. Please set up password first.")
        return

    iterations = 150_000
    password_attempt = getpass("Enter password to unlock function: ")
    key = derive_key(password_attempt, salt, iterations)
    try:
        encrypted_data = load_encrypted_data()
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        print("Credentials decrypted successfully:")
        unlock_function()
    except cryptography.fernet.InvalidToken:
        print("Incorrect password or corrupted data.")
    except Exception as e:
        print("An unexpected error occurred:", type(e).__name__, e)

def save_salt(salt: bytes):
    """ Save the salt to a file with restricted permissions """
    with open("salt.key", "wb") as salt_file:
        salt_file.write(salt)
    os.chmod("salt.key", 0o600)  ## Owner can read and write, no permissions for others

def load_salt() -> bytes:
    """ Load the salt from a file """
    with open("salt.key", "rb") as salt_file:
        return salt_file.read()

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """ Encrypt data using the derived key """
    fernet = Fernet(key)
    return fernet.encrypt(data)

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """ Decrypt data using the derived key """
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)

def save_encrypted_data(encrypted_data: bytes):
    """ Save encrypted data to a file with restricted permissions """
    with open("credentials.txt", "wb") as file:
        file.write(encrypted_data)
    os.chmod("credentials.txt", 0o600)  # Owner can read and write, no permissions for others

def load_encrypted_data() -> bytes:
    """ Load encrypted data from a file """
    with open("credentials.txt", "rb") as file:
        return file.read()

def unlock_function():
    """ Function that runs only if password verification is successful """
    print("Function unlocked and executed successfully!")

def main():
    action = input("Choose action (setup(s) or unlock(u)): ").strip().lower()
    if action == "setup" or action == "s":
        setup_password()
    elif action == "unlock" or action == "u":
        unlock_password()
    else:
        print("Invalid action.")
        
def auto_test():
    setup_password()
    unlock_password()

if __name__ == "__main__":
    # main()
    auto_test()
    
    
    
    
'''



'''