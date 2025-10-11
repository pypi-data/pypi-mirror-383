try:
    from . import encrypt_cython as _encrypt_impl
except ImportError:
    # Fallback to pure Python implementation if Cython module is not available
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import os
    import sys # Added import sys

    def generate_salt(length: int = 16) -> bytes:
        return os.urandom(length)

    def derive_key(password: str, salt: bytes, iterations: int = 100000, key_length: int = 32) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode("utf-8"))

    def encrypt_aes_gcm(data: bytes, key: bytes, associated_data: bytes = None) -> tuple[bytes, bytes, bytes]:
        if len(key) not in [16, 24, 32]:
            raise ValueError("AES key must be 16, 24, or 32 bytes long (128, 192, or 256 bits).")

        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return ciphertext, nonce, encryptor.tag

    def decrypt_aes_gcm(encrypted_data: bytes, key: bytes, nonce: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
        if len(key) not in [16, 24, 32]:
            raise ValueError("AES key must be 16, 24, or 32 bytes long (128, 192, or 256 bits).")

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)
        plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
        return plaintext

    _encrypt_impl = sys.modules[__name__] # Point to current module for fallback

generate_salt = _encrypt_impl.generate_salt
derive_key = _encrypt_impl.derive_key
encrypt_aes_gcm = _encrypt_impl.encrypt_aes_gcm
decrypt_aes_gcm = _encrypt_impl.decrypt_aes_gcm

