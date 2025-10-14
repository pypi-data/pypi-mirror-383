from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (.env).
    Centralized configuration for database, JWT, logging, and general app behavior.

    Attributes:
        app_name (str): Application name.
        app_description (str): Short description of the application.
        app_version (str): Application version.
        debug (bool): Enable debug mode (development only).
        database_url (str): Database connection URL.
        jwt_secret_key (str): Secret key for signing JWT tokens.
        jwt_algorithm (str): Algorithm used for JWT signing (default: HS256).
        jwt_access_token_expire_minutes (int): Expiration time for access tokens.
        jwt_refresh_token_expire_minutes (int): Expiration time for refresh tokens.
        login_url (str): URL endpoint for login.
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file (str): Path to the log file.
    """

    # App metadata
    app_name: str = "FastAPI Starter Pack"
    app_description: str = "A well-structured FastAPI starter with JWT auth"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database
    database_url: str

    # JWT configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_minutes: int = 1440
    login_url: str = "/auth/login"

    # Logging configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    class Config:
        """
        Pydantic configuration to load settings from `.env` file.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"  # Ensure proper encoding


# Singleton instance of settings for app-wide use
settings = Settings()
