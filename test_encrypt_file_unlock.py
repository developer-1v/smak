from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from base64 import urlsafe_b64encode
import os
from cryptography.fernet import Fernet
# from getpass import getpass
from custom_getpass import getpass

def key_from_password(password: str, salt: bytes = None) -> bytes:
    """ Generate a key from a password using PBKDF2, optionally using a provided salt """
    if salt is None:
        salt = os.urandom(16)  # Generate new salt if not provided
    # Perform key derivation
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    # Return the key and the salt encoded in URL-safe base64
    return urlsafe_b64encode(key), salt

def encrypt_file(file_path: str, key: bytes, salt: bytes) -> None:
    """ Encrypt a file and save the salt used """
    fernet = Fernet(key)
    with open(file_path, 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open(file_path, 'wb') as encrypted_file:
        encrypted_file.write(salt + encrypted)  # Prepend salt to encrypted data

def decrypt_file(file_path: str, password: str) -> bool:
    """ Decrypt a file using the password and the salt stored in the file """
    with open(file_path, 'rb') as file:
        salt = file.read(16)  # Read the salt from the start of the file
        encrypted = file.read()
    key, _ = key_from_password(password, salt)  # Regenerate the key using the stored salt
    fernet = Fernet(key)
    try:
        decrypted = fernet.decrypt(encrypted)
        with open(file_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted)
        return True
    except Exception as e:
        print("Failed to decrypt the file:", e)
        return False

def main_cmd():
    choice = input("Do you want to (E)ncrypt or (D)ecrypt? ")
    if choice.lower() not in ['e', 'd']:
        print("Invalid choice")
        return

    file_path = input("Enter the file path: ")
    password = getpass("Enter password: ")  # Uncomment this line for secure password input
    # password = 'test password'  # Comment or remove this line when using getpass

    if choice.lower() == 'e':
        key, salt = key_from_password(password)
        encrypt_file(file_path, key, salt)
        print("File encrypted successfully.")
    elif choice.lower() == 'd':
        if decrypt_file(file_path, password):
            print("File decrypted successfully.")
        else:
            print("Failed to decrypt the file.")

def main_automated(file_path, password=None):
    password = getpass("Enter password: ") if password is None else password
    key, salt = key_from_password(password)  # Unpack the key and salt
    encrypt_file(file_path, key, salt)
    input("Press enter to decrypt")
    decrypt_file(file_path, password)

if __name__ == "__main__":
    main_automated(
        'test_crypt_file.txt',
        # 'test password'
        )
    # main_cmd()
    # main_cmd()

