from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet
import os
from custom_getpass import getpass

def derive_key(password: str, salt: bytes, iterations: int = 100000) -> bytes:
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

def setup_password():
    """ Setup password and save salt and encrypted data """
    password = getpass("Set up password: ")
    salt = os.urandom(16)
    save_salt(salt)
    key = derive_key(password, salt)
    # Example data to encrypt
    data_to_encrypt = b"Example sensitive data"
    encrypted_data = encrypt_data(data_to_encrypt, key)
    save_encrypted_data(encrypted_data)
    print("Password setup complete and data encrypted.")

def unlock_password():
    """ Attempt to unlock with a password """
    salt = load_salt()
    print("Salt on Unlock:", salt)  # Debugging statement
    password_attempt = getpass("Enter password to unlock function: ")
    key = derive_key(password_attempt, salt)
    try:
        encrypted_data = load_encrypted_data()
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        print("Credentials decrypted successfully:", decrypted_data.decode())
        unlock_function()
    except Exception as e:
        print("Incorrect password or decryption error:", type(e).__name__, e)

def save_salt(salt: bytes):
    """ Save the salt to a file """
    with open("salt.key", "wb") as salt_file:
        salt_file.write(salt)

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
    """ Save encrypted data to a file """
    with open("credentials.txt", "wb") as file:
        file.write(encrypted_data)

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
    # setup_password()
    unlock_password()

if __name__ == "__main__":
    # main()
    auto_test()
    
    
    
    
'''
Security Concerns and Recommendations
1. Hardcoded Iteration Count:
The iteration count for the KDF is hardcoded to 100,000. While this is a reasonable number, it would be better to allow configuration based on the environment's security requirements and performance capabilities.
2. Lack of Secure Deletion:
When updating passwords or keys, the old salt and encrypted data files are overwritten but not securely deleted. This might allow recovery of previous values. Implementing secure deletion or using a more secure storage mechanism could mitigate this risk.
3. Debugging Information:
The application prints derived keys and salts during the setup and unlock processes. This is a significant security risk as it exposes sensitive information in logs or console outputs. It's recommended to remove or secure these debug statements.
4. Exception Handling:
The application catches a generic exception during decryption, which might obscure the source of errors. More specific exception handling could provide better error resolution and security response strategies.
5. File Storage Security:
The application does not implement encryption or secure permissions for the files storing the salt and encrypted data. Enhancing file security, for example, by setting appropriate file permissions or using encrypted file systems, would improve the security of these sensitive files.
6. Lack of Input Validation:
There is minimal validation of user inputs, which could potentially be exploited if the application is extended or integrated into a larger system. Implementing thorough input validation would enhance security.
7. Use of Default Backend:
The application uses a default cryptographic backend. Specifying a known secure backend or allowing configuration could provide more control over the cryptographic operations and their security properties.



'''