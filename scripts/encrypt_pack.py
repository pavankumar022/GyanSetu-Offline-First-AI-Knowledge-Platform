import os
from cryptography.fernet import Fernet

# Generates a key and saves it to a file
def generate_key(key_path: str = "secret.key"):
    key = Fernet.generate_key()
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    print(f"Key generated and saved to {key_path}")
    return key

# Loads the key from the current directory
def load_key(key_path: str = "secret.key") -> bytes:
    if not os.path.exists(key_path):
        return generate_key(key_path)
    with open(key_path, "rb") as key_file:
        return key_file.read()

# Encrypts a file
def encrypt_file(filename: str, key_path: str = "secret.key"):
    key = load_key(key_path)
    f = Fernet(key)
    
    with open(filename, "rb") as file:
        file_data = file.read()
        
    encrypted_data = f.encrypt(file_data)
    
    # Save the encrypted file
    with open(filename + ".enc", "wb") as file:
        file.write(encrypted_data)
    print(f"Encrypted file saved to {filename}.enc")

# Decrypts a file
def decrypt_file(filename: str, key_path: str = "secret.key"):
    key = load_key(key_path)
    f = Fernet(key)
    
    with open(filename, "rb") as file:
        encrypted_data = file.read()
        
    decrypted_data = f.decrypt(encrypted_data)
    
    # Save the decrypted file
    decrypted_filename = filename.replace(".enc", "")
    with open(decrypted_filename, "wb") as file:
        file.write(decrypted_data)
    print(f"Decrypted file saved to {decrypted_filename}")

if __name__ == "__main__":
    # Test script locally
    test_file = "test_data.txt"
    with open(test_file, "w") as f:
        f.write("Sensitive agricultural local intelligence cache.")
        
    print("Simulating on-device database encryption...")
    encrypt_file(test_file)
    decrypt_file(test_file + ".enc")
    
    # Clean up test files
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists(test_file + ".enc"):
        os.remove(test_file + ".enc")
    if os.path.exists("secret.key"):
        os.remove("secret.key")
    print("On-device encryption/decryption demo completed successfully.")
