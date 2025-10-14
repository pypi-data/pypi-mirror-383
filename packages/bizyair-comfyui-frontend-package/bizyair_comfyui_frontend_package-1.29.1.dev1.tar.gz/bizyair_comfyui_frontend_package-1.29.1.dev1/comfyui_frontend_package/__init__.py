from importlib.metadata import version, PackageNotFoundError

try:
    # Try the current package name first
    __version__ = version(__name__.split('.')[0])
except PackageNotFoundError:
    # Fallback to hardcoded name for backward compatibility
    try:
        __version__ = version("bizyair_comfyui_frontend_package")
    except PackageNotFoundError:
        __version__ = "unknown"
