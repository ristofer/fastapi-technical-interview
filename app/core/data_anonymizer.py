import base64

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class DataAnonymizer:
    def __init__(self, key: str | bytes) -> None:
        """
        Initialize the DataAnonymizer with a given AES key.

        Args:
            key (bytes or str): The AES key (must be 16, 24, or 32 bytes long).
                                If a string is provided, it will be encoded to bytes.
        """
        if isinstance(key, str):
            key = key.encode("utf-8")
        if len(key) not in (16, 24, 32):
            raise ValueError("The AES key must be either 16, 24, or 32 bytes long.")
        self.key = key

    def encrypt(self, plaintext: str, key: bytes = None) -> str:
        """
        Encrypt the plaintext using AES encryption in ECB mode with PKCS7 padding.
        This ensures that the same plaintext always encrypts to the same ciphertext.

        Args:
            plaintext (str): The plaintext string to encrypt.

        Returns:
            str: The URL-safe base64-encoded encrypted string.
        """
        padder = padding.PKCS7(128).padder()
        padded_plaintext = padder.update(plaintext.encode("utf-8")) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.ECB())

        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        encrypted_data = base64.urlsafe_b64encode(ciphertext).decode("utf-8")

        return encrypted_data

    def decrypt(self, encrypted_data: str, key: bytes = None) -> str:
        """
        Decrypt the encrypted data back to plaintext.

        Args:
            encrypted_data (str): The URL-safe base64-encoded encrypted string.

        Returns:
            str: The decrypted plaintext string.
        """
        ciphertext = base64.urlsafe_b64decode(encrypted_data)

        cipher = Cipher(algorithms.AES(key), modes.ECB())
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext_bytes.decode("utf-8")
