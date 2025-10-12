"""Bloret Launcher API Tool - A Python library for interacting with Bloret Launcher API."""

__version__ = "0.1.0"
__author__ = "Bloret"
__email__ = "contact@bloret.com"

from .core import Client, request_api
from .cli import main

__all__ = ["Client", "request_api", "main"]