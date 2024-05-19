from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import os
import base64
import hashlib
import bcrypt
from print_tricks import pt

class PasswordManager:
    def __init__(self, method='scrypt'):
        self.key_method = method
        self.len_salt = 32
        self.cpu_cost = 2**14
        self.block_size = 8
        self.parallelism = 1

    def encrypt_data(self, data, password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        key, _ = self.derive_key(password, salt)
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(data)
        return encrypted_data, salt

    def decrypt_data(self, encrypted_data, password, salt):
        key, _ = self.derive_key(password, salt)
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_data)

    def derive_key(self, password, salt=None):
        if isinstance(password, bytes):
            password_bytes = password
        else:
            password_bytes = password.encode('utf-8')
        
        if self.key_method == 'hkdf':
            kdf = HKDF(
                algorithm=hashes.SHA256(),
                length=self.len_salt,
                salt=salt,
                info=b'handshake data',
                backend=default_backend()
            )
        elif self.key_method == 'scrypt':
            kdf = Scrypt(
                salt=salt,
                length=self.len_salt,
                n=self.cpu_cost,
                r=self.block_size,
                p=self.parallelism,
                backend=default_backend()
            )
        elif self.key_method == 'sha256':
            salted_password = salt + password_bytes
            hashed_password = hashlib.sha256(salted_password).digest()
            return base64.urlsafe_b64encode(hashed_password), salt
        elif self.key_method == 'bcrypt':
            if salt is None:
                salt = bcrypt.gensalt()
            elif isinstance(salt, str):
                salt = salt.encode('utf-8')
            elif not isinstance(salt, bytes):
                salt = bcrypt.gensalt()

            hashed_password = bcrypt.hashpw(password_bytes, salt)
            return base64.urlsafe_b64encode(hashed_password), salt


        key = kdf.derive(password_bytes)
        return base64.urlsafe_b64encode(key), salt

    def store_hashed_password(self, hashed_password, salt, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if isinstance(salt, bytes):
            salt = salt.hex()
        encrypted_hash_salt, encryption_salt = self.encrypt_data(hashed_password + bytes.fromhex(salt), b'encryption_key')
        with open(file_path, 'wb') as f:
            f.write(encryption_salt + encrypted_hash_salt)

    def load_hashed_password(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        encryption_salt = data[:16]
        encrypted_hash_salt = data[16:]
        decrypted_hash_salt = self.decrypt_data(encrypted_hash_salt, b'encryption_key', encryption_salt)
        correct_hash = decrypted_hash_salt[:-len(encryption_salt)]
        return correct_hash, decrypted_hash_salt[-len(encryption_salt):].hex()
    
    def hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        elif isinstance(salt, str):
            salt = bytes.fromhex(salt)

        if isinstance(password, str):
            password = password.encode('utf-8')

        pt.t()
        key, salt_hex = self.derive_key(password, salt)
        pt.t()
        return key, salt_hex

    def verify_password(self, file_path, password_to_check):
        stored_hash, stored_salt = self.load_hashed_password(file_path)

        if isinstance(password_to_check, str):
            password_to_check = password_to_check.encode('utf-8')

        check_hash, _ = self.hash_password(password_to_check, stored_salt)

        if self.key_method == 'bcrypt':
            if bcrypt.checkpw(password_to_check, stored_hash):
                print("Password is correct.")
                self.perform_actions()
            else:
                print("Incorrect password.")
        else:
            if stored_hash == check_hash:
                print("Password is correct.")
                self.perform_actions()
            else:
                print("Incorrect password.")

    def perform_actions(self):
        print("Performing actions...")

if __name__ == '__main__':
    derive_methods = ['sha256', 'hkdf', 'scrypt', 'bcrypt']
    for method in derive_methods:
        pt(method)
        
        password_manager = PasswordManager(method=method)
        password = b"mysecretpassword"
        hashed_password, salt = password_manager.hash_password(password)
        file_path = 'path_to_secure_storage/password_hash.bin'
        password_manager.store_hashed_password(hashed_password, salt, file_path)
        pt.c('------START---------')
        password_manager.verify_password(file_path, password)
        pt.c('---------------')