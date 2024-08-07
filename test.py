from print_tricks import pt



''' pyside6 tests'''


import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtAxContainer import QAxWidget

class FileExplorerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Embedded File Explorer")

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create the ActiveX control for Windows File Explorer
        self.file_explorer = QAxWidget("Shell.Explorer.2")

        # Add the ActiveX control to the layout
        layout.addWidget(self.file_explorer)

        # Set the initial directory (e.g., C:\)
        self.file_explorer.dynamicCall("Navigate(const QString&)", "C:\\")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorerWindow()
    window.show()
    sys.exit(app.exec())










''' Cryptography tests'''

def run_tests():
    ...
    # basic_encrypt_decrypt(b"Hello, World!")
    pt.c('-----------')
    # password_encrypt_decrypt(b"mysecretpassword", b"Secret data")
    pt.c('-----------')
    # dpapi_encrypt_decrypt(b"Data to encrypt")
    pt.c('-----------')
    # challenge_response_test()
    pt.c('-----------')
    # password_hashing_test()
    pt.c('-----------')
    # password_hashing_test_with_more_secure_storage()
    pt.c('-----------')
    # password_hashing_test_with_encrypted_file_storage()
    pt.c('-----------')
    # password_hashing_test_with_encrypted_file_storage_and_derived_key()
    pt.c('-----------')
    # convert_to_ico('assets/icon.png', 'assets/icon.ico')
    pt.c('-----------')
    # convert_images_to_ico()
    pt.c('-----------')
    # profile_memory_test()
    pt.c('-----------')
    password_hashing_test_sha256()
    pt.c('-----------')
    password_hashing_w_salt_test_sha256()
    pt.c('-----------')
'''
Minimal Cryptography
'''

from cryptography.fernet import Fernet

def basic_encrypt_decrypt(data):
    # Generate a key
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    # Encrypt some data
    cipher_data = cipher_suite.encrypt(data)
    print("Encrypted:", cipher_data)

    # Decrypt the data
    decrypted_data = cipher_suite.decrypt(cipher_data)
    print("Decrypted:", decrypted_data)

# basic_encrypt_decrypt(b"Hello, World!")

''' 
Cryptography with password 
'''

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
import os
import base64

def password_encrypt_decrypt(password: bytes, data: bytes):
    # Generate a salt
    salt = os.urandom(16)

    # Derive a key from the password
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(password)
    fernet_key = Fernet(base64.urlsafe_b64encode(key))

    # Encrypt the data
    encrypted = fernet_key.encrypt(data)
    print("Encrypted:", encrypted)

    # Decrypt the data
    # Derive a key from the password
    kdf2 = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key2 = kdf2.derive(b'mysecretpassword')
    fernet_key2 = Fernet(base64.urlsafe_b64encode(key2))
    
    decrypted = fernet_key2.decrypt(encrypted)
    print("Decrypted:", decrypted)

# password_encrypt_decrypt(b"mysecretpassword", b"Secret data")

'''
Cryptography with Secured Key
'''

from cryptography.fernet import Fernet
import os
from win32crypt import CryptProtectData, CryptUnprotectData

def dpapi_encrypt_decrypt(data: bytes):
    # Generate a key
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    # Encrypt the data
    encrypted_data = cipher_suite.encrypt(data)
    print("Encrypted:", encrypted_data)

    # Use DPAPI to encrypt the key
    # Ensure the key is in the correct format and description is a string
    protected_key = CryptProtectData(key, "Description")

    # Decrypt the key using DPAPI
    unprotected_key = CryptUnprotectData(protected_key)
    new_cipher_suite = Fernet(unprotected_key[1])

    # Decrypt the data
    decrypted_data = new_cipher_suite.decrypt(encrypted_data)
    print("Decrypted:", decrypted_data)

# dpapi_encrypt_decrypt(b"Data to encrypt")



''' Challenge-response protocol '''

import hmac
import os
import hashlib

def generate_challenge():
    """ Generate a random challenge to send to the client. """
    return os.urandom(16)

def generate_response(challenge, password):
    """ Generate a response based on the challenge and the password. """
    return hmac.new(password, challenge, hashlib.sha256).digest()

def verify_response(challenge, client_response, password):
    """ Verify the client's response by recalculating it. """
    expected_response = generate_response(challenge, password)
    return hmac.compare_digest(expected_response, client_response)

def challenge_response_test():
    # Server side
    challenge = generate_challenge()

    # Client side
    password = b"mysecretpassword"
    response = generate_response(challenge, password)
    # Server side verification
    is_valid = verify_response(challenge, response, password)
    print("Password is valid:", is_valid)
    
# challenge_response_test()



'''
password hashing
'''

import bcrypt

def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed

def verify_password(stored_hash, password_to_check):
    # Check that an unhashed password matches one that has been hashed
    if bcrypt.checkpw(password_to_check, stored_hash):
        print("Password is correct. Executing function.")
        some_function()
    else:
        print("Incorrect password.")

def some_function():
    print("Function is now running.")

def password_hashing_test():
    # Example usage
    password = b"mysecretpassword"
    hashed_password = hash_password(password)
    # verify_password(hashed_password, password)
    
# password_hashing_test()

'''
password hashing with more secure storage
'''

import bcrypt
import os

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed

def store_hashed_password(hashed_password, file_path):
    # Ensure the directory is secure
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Set file permissions (this example is for Unix-like systems)
    open(file_path, 'wb').close()
    os.chmod(file_path, 0o600)
    with open(file_path, 'wb') as f:
        f.write(hashed_password)

def load_hashed_password(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def verify_password(file_path, password_to_check):
    stored_hash = load_hashed_password(file_path)
    if bcrypt.checkpw(password_to_check, stored_hash):
        print("Password is correct.")
    else:
        print("Incorrect password.")

def password_hashing_test_with_more_secure_storage():

    # Example usage
    password = b"mysecretpassword"
    hashed_password = hash_password(password)
    file_path = 'path_to_secure_storage/password_hash.bin'
    store_hashed_password(hashed_password, file_path)
    pt.t()
    verify_password(file_path, password)
    pt.t()

# password_hashing_test_with_more_secure_storage()

'''
password hashing with encrypted file storage
'''


from cryptography.fernet import Fernet
import bcrypt
import os

# Generate and save this key securely; load it when needed
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data):
    return cipher_suite.encrypt(data)

def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return encrypt_data(hashed)  # Encrypt the hash before storing it

def store_hashed_password(encrypted_hashed_password, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    open(file_path, 'wb').close()
    os.chmod(file_path, 0o600)
    with open(file_path, 'wb') as f:
        f.write(encrypted_hashed_password)

def load_hashed_password(file_path):
    with open(file_path, 'rb') as f:
        encrypted_hashed_password = f.read()
    return decrypt_data(encrypted_hashed_password)

def verify_password(file_path, password_to_check):
    stored_hash = load_hashed_password(file_path)
    if bcrypt.checkpw(password_to_check, stored_hash):
        print("Password is correct.")
    else:
        print("Incorrect password.")

def password_hashing_test_with_encrypted_file_storage():
    # Example usage
    password = b"mysecretpassword"
    hashed_password = hash_password(password)
    file_path = 'path_to_secure_storage/password_hash.bin'
    store_hashed_password(hashed_password, file_path)
    verify_password(file_path, password)

# password_hashing_test_with_encrypted_file_storage()   

'''
password hashing with encrypted file storage & derived key (no storage)
'''

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import bcrypt
import os
import base64

def derive_key(password):
    """ Derive a key from a password using Scrypt """
    salt = os.urandom(16)  # Generate a new salt
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(password)
    return base64.urlsafe_b64encode(key), salt

def store_hashed_password(hashed_password, salt, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Encrypt the hash and salt before storing
    encrypted_hash_salt, encryption_salt = encrypt_data(hashed_password + salt, b'encryption_key')
    with open(file_path, 'wb') as f:
        f.write(encryption_salt + encrypted_hash_salt)  # Store the encryption salt and the encrypted data together

def load_hashed_password(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    encryption_salt = data[:16]  # Assuming the salt size is 16 bytes
    encrypted_hash_salt = data[16:]
    decrypted_hash_salt = decrypt_data(encrypted_hash_salt, b'encryption_key', encryption_salt)
    salt = decrypted_hash_salt[:16]
    hashed_password = decrypted_hash_salt[16:]
    return hashed_password, salt

def encrypt_data(data, password):
    key, salt = derive_key(password)
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data)
    return encrypted_data, salt

def decrypt_data(encrypted_data, password, salt):
    key = derive_key_from_password_and_salt(password, salt)
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_data)

def derive_key_from_password_and_salt(password, salt):
    """ Re-derive the key from the password and salt """
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(password)
    return base64.urlsafe_b64encode(key)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed, salt


def verify_password(file_path, password_to_check):
    stored_hash, salt = load_hashed_password(file_path)
    if bcrypt.checkpw(password_to_check, stored_hash):
        print("Password is correct.")
        perform_actions()
    else:
        print("Incorrect password.")

def perform_actions():
    print("Performing actions...")

def password_hashing_test_with_encrypted_file_storage_and_derived_key():
    # Example usage
    password = b"mysecretpassword"
    hashed_password, salt = hash_password(password)
    file_path = 'path_to_secure_storage/password_hash.bin'
    store_hashed_password(hashed_password, salt, file_path)
    pt.t(3)
    verify_password(file_path, password)
    pt.t(3)

# password_hashing_test_with_encrypted_file_storage_and_derived_key()



'''
password hashing with SHA-256
'''

import hashlib

def hash_password1_sha256(password):
    """ Hash a password using SHA-256. """
    if isinstance(password, str):
        password = password.encode('utf-8')
    hashed = hashlib.sha256(password).hexdigest()
    return hashed.encode('utf-8')

def verify_password_sha256(stored_hash, password_to_check):
    """ Check that an unhashed password matches one that has been hashed with SHA-256 """
    if isinstance(password_to_check, str):
        password_to_check = password_to_check.encode('utf-8')
    hashed_check = hashlib.sha256(password_to_check).hexdigest().encode('utf-8')
    if hashed_check == stored_hash:
        print("Password is correct. Executing function.")
        some_function()
    else:
        print("Incorrect password.")

def some_function():
    print("Function is now running.")

def password_hashing_test_sha256():
    password = "mysecretpassword"
    hashed_password = hash_password1_sha256(password)
    pt.t('password hashing test sha256')
    verify_password_sha256(hashed_password, password)
    pt.t('password hashing test sha256')

# password_hashing_test_sha256()


'''
password hashing with SHA-256 and salting
'''

import hashlib
import os

def hash_password2_sha256(password):
    """ Hash a password using SHA-256 with a salt. """
    # Generate a random salt
    salt = os.urandom(16)
    # Ensure the password is a bytes object
    if isinstance(password, str):
        password = password.encode('utf-8')
    # Combine the salt and password
    salted_password = salt + password
    # Hash the salted password
    hashed = hashlib.sha256(salted_password).hexdigest()
    # Return the salt and the hashed password
    return salt, hashed.encode('utf-8')

def verify_password2_sha256(stored_salt, stored_hash, password_to_check):
    """ Check that an unhashed password matches one that has been hashed with SHA-256 """
    if isinstance(password_to_check, str):
        password_to_check = password_to_check.encode('utf-8')
    # Combine the salt and the password to check
    salted_password_to_check = stored_salt + password_to_check
    # Hash the salted password to check
    hashed_check = hashlib.sha256(salted_password_to_check).hexdigest().encode('utf-8')
    if hashed_check == stored_hash:
        print("Password is correct. Executing function.")
        some_function()
    else:
        print("Incorrect password.")

def some_function():
    print("Function is now running.")

def password_hashing_w_salt_test_sha256():
    password = "mysecretpassword"
    salt, hashed_password = hash_password2_sha256(password)
    pt.t('password hashing w/ salt Sha256')
    verify_password2_sha256(salt, hashed_password, password)
    pt.t('password hashing w/ salt Sha256')

# password_hashing_w_salt_test_sha256()





'''
Convert image to .ico icon

'''


import os
from PIL import Image
import sys

def convert_to_ico(input_path, output_path, sizes=[(64, 64)]):
    """
    Convert an image to ICO format.
    
    Args:
    input_path (str): The path to the input image file.
    output_path (str): The path where the .ico file will be saved.
    sizes (list): A list of tuple sizes for the icon.
    """
    with Image.open(input_path) as img:
        img.save(output_path, format='ICO', sizes=sizes)
# convert_images_to_ico()


'''
Convert multiple images to .ico icon

'''
def convert_images_to_ico():    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    assets_dir = os.path.join(dir_path, 'assets')

    # Loop through all files in the assets directory
    for file_name in os.listdir(assets_dir):
        if file_name.endswith('.png'):
            input_image = os.path.join(assets_dir, file_name)
            output_ico = os.path.join(assets_dir, file_name.replace('.png', '.ico'))
            
            convert_to_ico(input_image, output_ico)
# convert_images_to_ico()
            

'''
Profile memory of import statements

'''


from memory_profiler import profile

@profile
def import_modules():
    from print_tricks import pt
    
    import json, ctypes, threading, sys, os, time
    import tkinter as tk
    from tkinter import font, messagebox
    from pynput import keyboard, mouse
    from pystray import MenuItem as item, Icon, Menu, MenuItem
    from PIL import Image

def profile_memory_test():
    import_modules()

    # '''
    # python -m memory_profiler test.py
    # '''
    
# profile_memory_test()


if __name__ == "__main__":
    run_tests()

