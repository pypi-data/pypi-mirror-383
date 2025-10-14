"""SURFdrive file management tool."""

__version__ = "2025.1.9"

# Import main functions for user access
from .surfdrive_download import download_surfdrive_csv, main

__all__ = ["download_surfdrive_csv", "main"]
