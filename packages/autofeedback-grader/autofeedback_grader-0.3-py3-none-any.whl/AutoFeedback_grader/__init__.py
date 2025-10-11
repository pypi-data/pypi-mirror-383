from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("autofeedback_grader")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "unknown"