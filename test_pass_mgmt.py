from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import os
import base64
import hashlib
from print_tricks import pt

class CryptoManager:
    def __init__(self, method='scrypt', len_salt=32, cpu_cost=2**14, block_size=8, parallelism=1):
        self.key_method = method
        self.len_salt = len_salt
        self.cpu_cost = cpu_cost
        self.block_size = block_size
        self.parallelism = parallelism

    def derive_key(self, password, salt):
        if isinstance(password, bytes):
            password_bytes = password
        else:
            password_bytes = password.encode('utf-8')
        
        if isinstance(salt, bytes):
            salt_bytes = salt
        else:
            salt_bytes = salt.encode('utf-8')

        if self.key_method == 'hkdf':
            kdf = HKDF(
                algorithm=hashes.SHA256(),
                length=self.len_salt,
                salt=salt_bytes,
                info=b'handshake data',
                backend=default_backend()
            )
        elif self.key_method == 'scrypt':
            kdf = Scrypt(
                salt=salt_bytes,
                length=self.len_salt,
                n=self.cpu_cost,
                r=self.block_size,
                p=self.parallelism,
                backend=default_backend()
            )
        elif self.key_method == 'sha256':
            salted_password = salt_bytes + password_bytes
            hashed_password = hashlib.sha256(salted_password).digest()
            # pt(base64.urlsafe_b64encode(hashed_password))
            return base64.urlsafe_b64encode(hashed_password), salt

        key = kdf.derive(password_bytes)
        # pt(base64.urlsafe_b64encode(key))
        return base64.urlsafe_b64encode(key), salt

    def encrypt_data(self, secure_payload, secret_key, salt=None):
        pt(secure_payload, secret_key, salt)
        if salt is None:
            salt = os.urandom(16)
        key, _ = self.derive_key(secret_key, salt)
        cipher_suite = Fernet(key)
        encrypted_secure_payload = cipher_suite.encrypt(secure_payload)
        return encrypted_secure_payload, salt

    def decrypt_data(self, encrypted_secure_payload, secret_key, salt):
        key, _ = self.derive_key(secret_key, salt)
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_secure_payload)

class PasswordManager:
    def __init__(self, method='scrypt'):
        self.crypto_manager = CryptoManager(method=method)

    def store_hashed_password(self, hashed_password, salt, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if isinstance(salt, str):
            salt = bytes.fromhex(salt)
        encrypted_secure_payload, encryption_salt = self.crypto_manager.encrypt_data(
                                    hashed_password + salt, b'encryption_key'
                                    )
        with open(file_path, 'wb') as f:
            f.write(encryption_salt + encrypted_secure_payload)

    def load_hashed_password(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        encryption_salt = data[:16]
        encrypted_secure_payload = data[16:]
        decrypted_hash_salt = self.crypto_manager.decrypt_data(
                                    encrypted_secure_payload, b'encryption_key', encryption_salt
                                    )
        correct_hash = decrypted_hash_salt[:-len(encryption_salt)]
        return correct_hash, decrypted_hash_salt[-len(encryption_salt):].hex()

    def hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        elif isinstance(salt, str):
            salt = bytes.fromhex(salt)

        if isinstance(password, str):
            password = password.encode('utf-8')

        key, _ = self.crypto_manager.derive_key(password, salt)
        return key, salt.hex()

    def verify_password(self, file_path, password_to_check):
        stored_hash, stored_salt = self.load_hashed_password(file_path)

        if isinstance(password_to_check, str):
            password_to_check = password_to_check.encode('utf-8')

        check_hash, _ = self.crypto_manager.derive_key(password_to_check, bytes.fromhex(stored_salt))
        return check_hash == stored_hash

    def perform_actions(self):
        # Example action: verify a password
        file_path = 'path/to/password/file'
        user_password = 'user_input_password'
        verification_result = self.verify_password(file_path, user_password)
        print("Password verification result:", verification_result)
        
        
if __name__ == '__main__':
    derive_methods = ['sha256', 'hkdf', 'scrypt']
    for method in derive_methods:
        password_manager = PasswordManager(method=method)
        password = b"mysecretpassword"
        hashed_password, salt = password_manager.hash_password(password)
        file_path = 'path_to_secure_storage/password_hash.bin'
        password_manager.store_hashed_password(hashed_password, salt, file_path)
        
        pt.t(method)
        if password_manager.verify_password(file_path, password):
            pt.t(method)
            print("Password verification successful.")
        else:
            print("Password verification failed.")