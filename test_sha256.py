'''
password hashing with encrypted file storage & derived key (no storage)
'''
from print_tricks import pt

pt.c('-----------')
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet
import os
import base64

len_salt = 16
cpu_cost = 2**14
block_size = 8
parallelism = 1

len_salt = 32
cpu_cost = 2
block_size = 4
parallelism = 1

def derive_key(password):
    """ Derive a key from a password using Scrypt """
    salt = os.urandom(16)  # Generate a new salt
    kdf = Scrypt(
        salt=salt,
        length=len_salt,
        n=cpu_cost,
        r=block_size,
        p=parallelism,
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
        length=len_salt,
        n=cpu_cost,
        r=block_size,
        p=parallelism,
        backend=default_backend()
    )
    key = kdf.derive(password)
    return base64.urlsafe_b64encode(key)

def hash_password(password):
    salt = os.urandom(16)
    kdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=None,
        backend=default_backend()
    )
    hashed = kdf.derive(password)
    return hashed, salt

def load_hashed_password(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    encryption_salt = data[:16]  # Assuming the salt size is 16 bytes
    encrypted_hash_salt = data[16:]
    decrypted_hash_salt = decrypt_data(encrypted_hash_salt, b'encryption_key', encryption_salt)
    # Assuming the correct hash is the first complete hash in the decrypted data
    correct_hash = decrypted_hash_salt[:32]  # Assuming SHA256 hash length
    print("Correct Hash:", correct_hash)  # Debug print to check the format
    return correct_hash

def verify_password(file_path, password_to_check):
    stored_hash = load_hashed_password(file_path)
    print("Stored Hash for Verification:", stored_hash)  # Debug print to check the format
    if stored_hash == hash_password(password_to_check)[0]:
        print("Password is correct.")
        perform_actions()
    else:
        print("Incorrect password.")

def perform_actions():
    print("Performing actions...")

# Example usage
password = b"mysecretpassword"
hashed_password, salt = hash_password(password)
file_path = 'path_to_secure_storage/password_hash.bin'
store_hashed_password(hashed_password, salt, file_path)
pt.t(3)
verify_password(file_path, password)
pt.t(3)