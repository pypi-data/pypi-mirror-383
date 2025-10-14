from passlib.context import CryptContext

# Configure passlib to use bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a given password using bcrypt.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    """
    Verify that a given plain text password matches a hashed password.

    Args:
        plain_password (str): The plain text password to be verified.
        hashed_password (str): The hashed password to be verified against.

    Returns:
        bool: Whether the plain text password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
