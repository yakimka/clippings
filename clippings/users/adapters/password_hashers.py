import hashlib
import hmac
import os

from clippings.users.ports import PasswordHasherABC


class PBKDF2PasswordHasher(PasswordHasherABC):
    def __init__(self, iterations: int = 50_000, salt_length: int = 16):
        self.iterations = iterations
        self.salt_length = salt_length
        self.algorithm = "sha1"
        self.hash_length = 20

    def hash(self, password: str) -> str:
        salt = os.urandom(self.salt_length)
        hashed_password = hashlib.pbkdf2_hmac(
            self.algorithm,
            password.encode("utf-8"),
            salt,
            self.iterations,
            dklen=self.hash_length,
        )
        return f"{salt.hex()}:{hashed_password.hex()}"

    def verify(self, password: str, hashed_password: str) -> bool:
        try:
            salt_hex, hash_hex = hashed_password.split(":")
            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)

            new_hash = hashlib.pbkdf2_hmac(
                self.algorithm,
                password.encode("utf-8"),
                salt,
                self.iterations,
                dklen=self.hash_length,
            )
            return hmac.compare_digest(new_hash, stored_hash)
        except ValueError:
            return False
