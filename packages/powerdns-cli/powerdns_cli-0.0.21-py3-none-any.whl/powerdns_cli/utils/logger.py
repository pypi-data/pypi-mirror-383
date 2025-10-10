"""A custom logging handler module for collecting logs, messages, and success statuses.

This module provides the `ResultHandler` class, which extends `logging.Handler` to accumulate
log records,custom messages, and success statuses in a structured dictionary.
"""

import json
import logging
from typing import Any

import click
import requests


class ResultHandler(logging.Handler):
    """A custom logging handler that collects logs, a message, and a success status.

    Attributes:
        result (Dict[str, Any]): A dictionary storing logs, a message, and a success status.
    """

    def __init__(self) -> None:
        """Initializes the ResultHandler with default values for the result dictionary."""
        super().__init__()
        self.result: dict[str, Any] = {
            "logs": [],
            "message": "",
            "success": None,
            "http": [],
            "data": None,
        }

    def emit(self, record: logging.LogRecord) -> None:
        """Appends the formatted log record to the logs list.

        Args:
            record (logging.LogRecord): The log record to format and append.
        """
        self.result["logs"].append(self.format(record))

    def set_data(self, response: requests.Response) -> None:
        """Sets the data in the result dictionary.

        Args:
            response: A requests response which contains the return data in its json answer.
        """
        try:
            self.result["data"] = response.json()
        except json.JSONDecodeError:
            self.result["data"] = response.text

    def set_message(self, message: str) -> None:
        """Sets the message in the result dictionary.

        Args:
            message (str): The message to set.
        """
        self.result["message"] = message

    def log_http_data(self, ctx: click.Context, response: requests.Response) -> None:
        """Sets the data in the result dictionary.

        Args:
            ctx: A click context object to save the response data to.
            response: A requests.Response object.
        """
        response_data = {"status_code": response.status_code, "reason": response.reason}
        try:
            response_data["json"] = response.json()
            response_data["text"] = ""
        except json.JSONDecodeError:
            response_data["json"] = {}
            response_data["text"] = response.text
        if ctx and ctx.obj.config["debug"]:
            request_data = {
                "method": response.request.method,
                "body": json.loads(response.request.body) if response.request.body else "",
                "url": response.request.url,
            }
        else:
            request_data = {}
        http_log = {"response": response_data, "request": request_data}
        self.result["http"].append(http_log)

    def set_success(self, success: bool = True) -> None:
        """Sets the success status to True in the result dictionary."""
        self.result["success"] = success

    def get_result(self) -> dict[str, Any]:
        """Returns the current result dictionary.

        Returns:
            Dict[str, Any]: The result dictionary containing logs, message, and success status.
        """
        return self.result
