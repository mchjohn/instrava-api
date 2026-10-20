from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Configure password hasher with Argon2id
_password_hasher = PasswordHash((Argon2Hasher(),))


def get_password_hash(password: str) -> str:
    """Generate an Argon2id hash for the given plain text password."""
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against an Argon2id hash."""
    return _password_hasher.verify(plain_password, hashed_password)
