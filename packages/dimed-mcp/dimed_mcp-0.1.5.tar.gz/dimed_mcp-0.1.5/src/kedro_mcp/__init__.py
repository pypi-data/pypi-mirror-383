from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("dimed-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
