"""AI Shell Command Generator - AI-powered shell command generation."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ai-shell-command-generator")
except PackageNotFoundError:
    # Package not installed, development mode
    __version__ = "dev"

from ai_shell_command_generator.main import main

__all__ = ["main", "__version__"]
