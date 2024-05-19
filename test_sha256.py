'''
password hashing with encrypted file storage & derived key (no storage)
'''
from print_tricks import pt

pt.c('-----------')
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os
import base64

len_salt = 32
cpu_cost = 2**14
block_size = 8
parallelism = 1

# len_salt = 32
# cpu_cost = 2
# block_size = 4
# parallelism = 1




def encrypt_data(data, password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    key, _ = derive_key(password, salt)
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data)
    return encrypted_data, salt

def decrypt_data(encrypted_data, password, salt):
    key, _ = derive_key(password, salt)
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_data)

def derive_key(password, salt):
    """ Derive a key from a password using Scrypt with a given salt """
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
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    encrypted_hash_salt, encryption_salt = encrypt_data(hashed_password + salt, b'encryption_key')
    with open(file_path, 'wb') as f:
        f.write(encryption_salt + encrypted_hash_salt)

def load_hashed_password(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    encryption_salt = data[:16]
    encrypted_hash_salt = data[16:]
    decrypted_hash_salt = decrypt_data(encrypted_hash_salt, b'encryption_key', encryption_salt)
    correct_hash = decrypted_hash_salt[:-len(encryption_salt)]  # Assuming salt is at the end
    return correct_hash, decrypted_hash_salt[-len(encryption_salt):].hex()

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    elif isinstance(salt, str):
        salt = bytes.fromhex(salt)

    if isinstance(password, str):
        password = password.encode('utf-8')

    key, _ = derive_key(password, salt)
    return key, salt.hex()

def verify_password(file_path, password_to_check):
    stored_hash, stored_salt = load_hashed_password(file_path)
    # stored_hash, stored_salt = hash_password(password_to_check)
    print("Stored Hash for Verification:", stored_hash)
    print("Stored Salt for Verification:", stored_salt)

    if isinstance(password_to_check, str):
        password_to_check = password_to_check.encode('utf-8')

    check_hash, _ = hash_password(password_to_check, stored_salt)
    print("Recomputed Hash for Verification:", check_hash)
    print("Recomputed Salt for Verification:", stored_salt)

    if stored_hash == check_hash:
        print("Password is correct.")
        perform_actions()
    else:
        print("Incorrect password.")

def perform_actions():
    print("Performing actions...")


password = b"mysecretpassword"
hashed_password, salt = hash_password(password)
file_path = 'path_to_secure_storage/password_hash.bin'
store_hashed_password(hashed_password, salt, file_path)
pt.t(3)
verify_password(file_path, password)
pt.t(3)