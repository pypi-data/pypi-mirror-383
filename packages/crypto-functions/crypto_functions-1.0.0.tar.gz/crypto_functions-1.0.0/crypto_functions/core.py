"""
crypto_functions.py
-----------------
Secure hashing and encryption utilities for Python.

Functions:
- hash_argon2(password)
- hash_sha256(data)
- encrypt_file(in_file, password, out_file)
- decrypt_file(enc_file, password, out_file)
"""

from argon2 import PasswordHasher
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import os


def hash_argon2(password: str) -> str:
    """
    Hash a password using Argon2 (secure for credentials).
    Args:
        password (str): The password to hash.
    Returns:
        str: The Argon2 hash string.
    """
    ph = PasswordHasher()
    return ph.hash(password)


def hash_sha256(data: str) -> str:
    """
    Generate a SHA256 hash of input data.
    Args:
        data (str): Input string to hash.
    Returns:
        str: Hexadecimal representation of the hash.
    """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data.encode())
    return digest.finalize().hex()


def encrypt_file(in_file: str, password: str, out_file: str) -> None:
    """
    Encrypt a file using AES-GCM with a password.
    Args:
        in_file (str): Path of the input file to encrypt.
        password (str): Password to derive encryption key.
        out_file (str): Path to save encrypted output.
    """
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=500_000,
    )
    key = kdf.derive(password.encode())

    with open(in_file, "rb") as f:
        data = f.read()

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, None)

    with open(out_file, "wb") as f:
        f.write(salt + nonce + ct)


def decrypt_file(enc_file: str, password: str, out_file: str) -> bool:
    """
    Decrypt a file encrypted with AES-GCM and PBKDF2 key.
    Args:
        enc_file (str): Path to encrypted file.
        password (str): Password used during encryption.
        out_file (str): Path to save decrypted file.
    Returns:
        bool: True if successful, False if password incorrect.
    """
    with open(enc_file, "rb") as f:
        blob = f.read()

    salt, nonce, ct = blob[:16], blob[16:28], blob[28:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=500_000,
    )
    key = kdf.derive(password.encode())
    aesgcm = AESGCM(key)

    try:
        data = aesgcm.decrypt(nonce, ct, None)
        with open(out_file, "wb") as f:
            f.write(data)
        return True
    except InvalidTag:
        print("❌ Error: Incorrect password or corrupted file.")
        return False
