from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("fastapi-starter-kit")
except PackageNotFoundError:
    # fallback if running from source without install
    try:
        from ._version import version as __version__
    except ImportError:
        __version__ = "0.0.0"
