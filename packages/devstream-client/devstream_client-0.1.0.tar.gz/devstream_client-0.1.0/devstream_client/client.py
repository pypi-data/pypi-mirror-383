"""
DevStream client for sending logs to the DevStream service.
"""

import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime


class DevStreamClient:
    """Client for sending logs to DevStream service."""

    def __init__(
        self,
        api_key: str,
        app_key: str,
        deployment_key: str,
        base_url: str = "http://localhost:8787",
    ):
        """
        Initialize DevStream client.

        Args:
            api_key: API key for authentication
            app_key: Application key
            deployment_key: Deployment environment (e.g., 'local', 'dev', 'prod')
            base_url: Base URL of DevStream service
        """
        self.api_key = api_key
        self.app_key = app_key
        self.deployment_key = deployment_key
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/api/logs/ingest"

    def log(
        self,
        message: str,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> bool:
        """
        Send a log message to DevStream.

        Args:
            message: Log message content
            tags: Optional list of tags as dictionaries with 'name' and 'value' keys

        Returns:
            True if successful, False otherwise
        """
        payload = {
            "api_key": self.api_key,
            "app_key": self.app_key,
            "deployment_key": self.deployment_key,
            "message": message,
            "tags": tags or [],
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"X-API-Key": self.api_key},
                timeout=5,
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            # Log error but don't raise to avoid breaking application
            print(f"DevStream: Failed to send log: {e}")
            return False

    def log_with_tags(
        self,
        message: str,
        **kwargs: str,
    ) -> bool:
        """
        Send a log message with tags specified as keyword arguments.

        Args:
            message: Log message content
            **kwargs: Tags as keyword arguments (e.g., level="error", user_id="123")

        Returns:
            True if successful, False otherwise
        """
        tags = [{"name": k, "value": str(v)} for k, v in kwargs.items()]
        return self.log(message, tags)


class DevStreamHandler(logging.Handler):
    """Python logging handler for DevStream."""

    def __init__(
        self,
        api_key: str,
        app_key: str,
        deployment_key: str,
        base_url: str = "http://localhost:8787",
        extra_tags: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize DevStream logging handler.

        Args:
            api_key: API key for authentication
            app_key: Application key
            deployment_key: Deployment environment
            base_url: Base URL of DevStream service
            extra_tags: Additional tags to include with every log
        """
        super().__init__()
        self.client = DevStreamClient(api_key, app_key, deployment_key, base_url)
        self.extra_tags = extra_tags or {}

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to DevStream.

        Args:
            record: Log record to emit
        """
        try:
            message = self.format(record)
            tags = {
                "level": record.levelname,
                "logger": record.name,
                "module": record.module,
                **self.extra_tags,
            }

            # Add exception info if present
            if record.exc_info:
                tags["exception"] = "true"

            self.client.log_with_tags(message, **tags)
        except Exception:
            # Silently fail to avoid breaking the application
            self.handleError(record)


def devstream_logger(
    name: str,
    api_key: str,
    app_key: str,
    deployment_key: str,
    base_url: str = "http://localhost:8787",
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Create a logger with DevStream handler configured.

    Args:
        name: Logger name
        api_key: API key for authentication
        app_key: Application key
        deployment_key: Deployment environment
        base_url: Base URL of DevStream service
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = DevStreamHandler(api_key, app_key, deployment_key, base_url)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
