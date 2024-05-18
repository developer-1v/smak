
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

basic_encrypt_decrypt(b"Hello, World!")

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
    decrypted = fernet_key.decrypt(encrypted)
    print("Decrypted:", decrypted)

password_encrypt_decrypt(b"mysecretpassword", b"Secret data")

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

dpapi_encrypt_decrypt(b"Data to encrypt")

'''
Convert image to .ico icon

'''

# import os
# from PIL import Image
# import sys

# def convert_to_ico(input_path, output_path, sizes=[(64, 64)]):
#     """
#     Convert an image to ICO format.
    
#     Args:
#     input_path (str): The path to the input image file.
#     output_path (str): The path where the .ico file will be saved.
#     sizes (list): A list of tuple sizes for the icon.
#     """
#     with Image.open(input_path) as img:
#         img.save(output_path, format='ICO', sizes=sizes)

# if __name__ == "__main__":
#     # Get the directory of the current script
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     assets_dir = os.path.join(dir_path, 'assets')

#     # Loop through all files in the assets directory
#     for file_name in os.listdir(assets_dir):
#         if file_name.endswith('.png'):
#             input_image = os.path.join(assets_dir, file_name)
#             output_ico = os.path.join(assets_dir, file_name.replace('.png', '.ico'))
            
#             convert_to_ico(input_image, output_ico)


'''
Profile memory of import statements

'''

# from memory_profiler import profile

# @profile
# def import_modules():
#     from print_tricks import pt
    
#     import json, ctypes, threading, sys, os, time
#     import tkinter as tk
#     from tkinter import font, messagebox
#     from pynput import keyboard, mouse
#     from pystray import MenuItem as item, Icon, Menu, MenuItem
#     from PIL import Image

# # Call the function to execute the imports and profile them
# import_modules()

# '''
# python -m memory_profiler test.py
# '''