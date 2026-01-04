"""Utility modules."""
from .api_client import EODHDClient
from .file_handler import FileHandler
from .logger import DownloadLogger
from .data_loader import DataLoader  # <--- NEW

__all__ = ['EODHDClient', 'FileHandler', 'DownloadLogger', 'DataLoader']