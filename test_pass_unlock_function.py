import os
from base64 import urlsafe_b64encode
import re

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from secure_delete import secure_delete

from custom_getpass import getpass


## key derivation
derive_key_iterations = 150_000

## password requirements
min_pass_length = 1
require_letters = False
require_digits = False
require_capitals = False
require_symbols = False

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

def secure_delete_file(file_path: str, passes: int = 3):
    """ Overwrite the file with random data and then delete it using secure delete library"""
    secure_delete(file_path, passes=passes)

def update_salt(salt: bytes):
    """ Securely update the salt file """
    if os.path.exists("salt.key"):
        secure_delete_file("salt.key")
    save_salt(salt)

def update_encrypted_data(encrypted_data: bytes):
    """ Securely update the encrypted data file """
    if os.path.exists("credentials.txt"):
        secure_delete_file("credentials.txt")
    save_encrypted_data(encrypted_data)


def sanitize_password(password: str) -> str:
    """ Sanitize the password to ensure it contains only allowed characters. """
    allowed_pattern = re.compile(r'^[A-Za-z0-9@#$%^&+=]*$')
    if not allowed_pattern.match(password):
        raise ValueError("Password contains invalid characters.")
    return password

def validate_password(password: str) -> bool:
    """ Validate the password to ensure it meets the criteria, including sanitization. """
    try:
        password = sanitize_password(password)
    except ValueError as e:
        print(e)
        return False

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

    # Generate random data instead of using hardcoded sensitive data
    data_to_encrypt = os.urandom(32)  # 32 bytes of random data
    key = derive_key(password, salt, derive_key_iterations)
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

    password_attempt = getpass("Enter password to unlock function: ")
    key = derive_key(password_attempt, salt, derive_key_iterations)
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


def ensure_directory():
    """ Ensure the SMAK directory exists in the user's app data folder """
    # More robust handling of APPDATA environment variable
    app_data = os.getenv('APPDATA')
    if not app_data:
        raise EnvironmentError("APPDATA environment variable not set.")
    
    app_data_path = os.path.join(app_data, 'SMAK')
    if not os.path.exists(app_data_path):
        os.makedirs(app_data_path)
    return app_data_path

def save_salt(salt: bytes):
    """ Save the salt to a file with restricted permissions """
    salt_path = os.path.join(ensure_directory(), 'salt.key')
    # Create file with restricted permissions securely
    fd = os.open(salt_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as salt_file:
        salt_file.write(salt)

def save_encrypted_data(encrypted_data: bytes):
    """ Save encrypted data to a file with restricted permissions """
    data_path = os.path.join(ensure_directory(), 'credentials.txt')
    # Create file with restricted permissions securely
    fd = os.open(data_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as file:
        file.write(encrypted_data)

def load_salt() -> bytes:
    """ Load the salt from a file """
    salt_path = os.path.join(ensure_directory(), 'salt.key')
    with open(salt_path, "rb") as salt_file:
        return salt_file.read()

def load_encrypted_data() -> bytes:
    """ Load encrypted data from a file """
    data_path = os.path.join(ensure_directory(), 'credentials.txt')
    with open(data_path, "rb") as file:
        return file.read()

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """ Encrypt data using the derived key """
    fernet = Fernet(key)
    return fernet.encrypt(data)

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """ Decrypt data using the derived key """
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)

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