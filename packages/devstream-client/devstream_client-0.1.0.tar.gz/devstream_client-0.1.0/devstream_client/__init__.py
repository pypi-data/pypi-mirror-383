"""
DevStream Python Client Library

Simple logging client for DevStream service.
"""

from .client import DevStreamClient, devstream_logger

__version__ = "0.1.0"
__all__ = ["DevStreamClient", "devstream_logger"]
