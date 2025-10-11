import os

# Import Python objects for type hinting in cdef functions
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

cdef bytes _generate_salt(int length):
    return os.urandom(length)

def generate_salt(length: int = 16) -> bytes:
    return _generate_salt(length)

cdef bytes _derive_key(bytes password_bytes, bytes salt, int iterations, int key_length):
    cdef object kdf # Declare as object
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password_bytes)

def derive_key(password: str, salt: bytes, iterations: int = 100000, key_length: int = 32) -> bytes:
    return _derive_key(password.encode("utf-8"), salt, iterations, key_length)

cdef tuple _encrypt_aes_gcm(bytes data, bytes key, bytes associated_data):
    cdef bytes nonce
    cdef object cipher # Declare as object
    cdef object encryptor
    cdef bytes ciphertext

    if len(key) not in [16, 24, 32]:
        raise ValueError("AES key must be 16, 24, or 32 bytes long (128, 192, or 256 bits).")

    nonce = os.urandom(12) # GCM recommended nonce size is 12 bytes

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    if associated_data:
        encryptor.authenticate_additional_data(associated_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return ciphertext, nonce, encryptor.tag

def encrypt_aes_gcm(data: bytes, key: bytes, associated_data: bytes = None) -> tuple[bytes, bytes, bytes]:
    return _encrypt_aes_gcm(data, key, associated_data)

cdef bytes _decrypt_aes_gcm(bytes encrypted_data, bytes key, bytes nonce, bytes tag, bytes associated_data):
    cdef object cipher # Declare as object
    cdef object decryptor
    cdef bytes plaintext

    if len(key) not in [16, 24, 32]:
        raise ValueError("AES key must be 16, 24, or 32 bytes long (128, 192, or 256 bits).")

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    if associated_data:
        decryptor.authenticate_additional_data(associated_data)
    plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
    return plaintext

def decrypt_aes_gcm(encrypted_data: bytes, key: bytes, nonce: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
    return _decrypt_aes_gcm(encrypted_data, key, nonce, tag, associated_data)

