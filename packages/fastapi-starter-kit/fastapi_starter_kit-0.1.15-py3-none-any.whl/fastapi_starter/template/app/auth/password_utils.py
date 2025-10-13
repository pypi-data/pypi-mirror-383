import hashlib
from passlib.context import CryptContext

# Configure passlib to use bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain password safely using a two-step process:
    1. Pre-hash the password with SHA-256 to handle any length safely.
    2. Hash the SHA-256 digest with bcrypt for secure storage.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password ready to store in the database.
    """
    # Pre-hash password using SHA256
    sha256_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    # Hash the SHA256 string with bcrypt
    return pwd_context.hash(sha256_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a stored hashed password.

    Steps:
    1. Pre-hash the plain password with SHA-256 (same as in hash_password).
    2. Verify the SHA-256 hash against the stored bcrypt hash.

    Args:
        plain_password (str): The password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if password matches, False otherwise.
    """
    # Pre-hash the plain password using SHA256
    sha256_password = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(sha256_password, hashed_password)
