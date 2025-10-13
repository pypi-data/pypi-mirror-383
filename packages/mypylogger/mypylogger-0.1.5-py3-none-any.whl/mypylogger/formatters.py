"""
Copyright (c) 2024 Stephen Abbot. Licensed under MIT License.

Custom JSON formatters for structured logging.
"""

import json
import logging
import os
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any, Dict, List


def _create_fallback_jsonlogger() -> Any:
    """Create fallback JSON logger when pythonjsonlogger is not available."""
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from pythonjsonlogger import json as jsonlogger

        return jsonlogger
    else:

        class _JsonLoggerStub:
            class JsonFormatter(logging.Formatter):
                def __init__(self, *args: Any, **kwargs: Any) -> None:
                    super().__init__(*args, **kwargs)

                def format(self, record: logging.LogRecord) -> str:
                    return super().format(record)

        return _JsonLoggerStub()


try:
    from pythonjsonlogger import json as jsonlogger
except ImportError:
    # Fallback implementation when pythonjsonlogger is not available
    jsonlogger = _create_fallback_jsonlogger()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with fixed field order and processing.

    This formatter extends pythonjsonlogger.JsonFormatter to provide:
    - Fixed field order with 'time' always first
    - UTC timestamps in ISO8601 format with milliseconds
    - Removal of unwanted fields
    - Consistent field processing (e.g., line numbers as strings)

    The output JSON format is optimized for log parsing and analysis tools.

    Attributes:
        FIELD_ORDER (List[str]): Ordered list of fields to include in JSON output.
        UNWANTED_FIELDS (Set[str]): Set of fields to exclude from JSON output.
    """

    # Fixed field order with time first
    FIELD_ORDER = ["time", "levelname", "message", "filename", "lineno", "funcName"]

    # Fields to remove from output
    UNWANTED_FIELDS = {
        "taskName",
        "thread",
        "threadName",
        "process",
        "processName",
        "module",
        "pathname",
        "created",
        "msecs",
        "relativeCreated",
        "name",  # Use app name from config instead
        "msg",  # Use processed message instead
        "args",  # Raw args not needed in output
        "levelno",  # Use levelname instead
        "exc_info",  # Will be handled separately if needed
        "exc_text",
        "stack_info",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the formatter with default format if none provided."""
        # Set default format string if not provided
        if not args and "fmt" not in kwargs:
            # Create format string with our desired fields
            fmt = " ".join(f"%({field})s" for field in self.FIELD_ORDER)
            kwargs["fmt"] = fmt

        super().__init__(*args, **kwargs)

    def parse(self) -> List[str]:
        """Parse format string to determine field order with time always first."""
        # Get the original parsed fields
        original_fields = super().parse() if hasattr(super(), "parse") else []

        # Start with time first
        ordered_fields = ["time"]

        # Add other fields from FIELD_ORDER that are in the original fields
        for field in self.FIELD_ORDER[1:]:  # Skip 'time' since it's already first
            if field in original_fields or field in [
                "levelname",
                "message",
                "filename",
                "lineno",
                "funcName",
            ]:
                if field not in ordered_fields:
                    ordered_fields.append(field)

        # Add any remaining fields from original that aren't in our order
        for field in original_fields:
            if field not in ordered_fields and field not in self.UNWANTED_FIELDS:
                ordered_fields.append(field)

        return ordered_fields

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add fields to log record in the correct order."""
        # Add basic fields from the record
        log_record.update(message_dict)

        # Add standard logging fields
        log_record["levelname"] = record.levelname
        log_record["lineno"] = record.lineno

        # Add timestamp in UTC ISO8601 format with milliseconds
        log_record["time"] = self._format_timestamp(record)

        # Add filename (basename of pathname)
        if hasattr(record, "pathname") and record.pathname:
            log_record["filename"] = os.path.basename(record.pathname)
        elif hasattr(record, "filename"):
            log_record["filename"] = record.filename
        else:
            log_record["filename"] = "unknown"

        # Ensure funcName is present
        if not hasattr(record, "funcName") or record.funcName is None:
            log_record["funcName"] = "unknown"
        else:
            log_record["funcName"] = record.funcName

        # Handle exception information if present
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        elif record.exc_text:
            log_record["exc_info"] = record.exc_text

        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in log_record and key not in self.UNWANTED_FIELDS:
                log_record[key] = value

    def process_log_record(self, log_record: Dict[str, Any]) -> Dict[str, Any]:
        """Process log record with custom field handling."""
        # Remove unwanted fields
        for field in self.UNWANTED_FIELDS:
            log_record.pop(field, None)

        # Convert line numbers to strings
        if "lineno" in log_record:
            log_record["lineno"] = str(log_record["lineno"])

        # Handle None values - convert to empty string or remove
        for key, value in list(log_record.items()):
            if value is None:
                log_record[key] = ""

        # Ensure field order with time first
        ordered_record = OrderedDict()

        # Add fields in our specified order
        for field in self.FIELD_ORDER:
            if field in log_record:
                ordered_record[field] = log_record[field]

        # Add any remaining fields
        for key, value in log_record.items():
            if key not in ordered_record:
                ordered_record[key] = value

        return ordered_record

    def _format_timestamp(self, record: logging.LogRecord) -> str:
        """Format timestamp as UTC ISO8601 with milliseconds and 'Z' suffix."""
        # Get timestamp from record
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc)

        # Format as ISO8601 with milliseconds
        # Use manual formatting to ensure milliseconds are always 3 digits
        formatted = timestamp.strftime("%Y-%m-%dT%H:%M:%S")

        # Add milliseconds (3 digits)
        milliseconds = int(record.msecs)
        formatted += f".{milliseconds:03d}Z"

        return formatted

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        # Create the log record dict
        log_record: Dict[str, Any] = {}

        # Add basic message
        message_dict = {}
        if record.args:
            message_dict = {"message": record.getMessage()}
        else:
            message_dict = {"message": record.msg}

        # Add all fields
        self.add_fields(log_record, record, message_dict)

        # Process the log record (field ordering, cleanup, etc.)
        processed_record = self.process_log_record(log_record)

        # Convert to JSON
        try:
            return json.dumps(
                processed_record, ensure_ascii=False, separators=(",", ":")
            )
        except (TypeError, ValueError) as e:
            # Fallback to basic formatting if JSON serialization fails
            return json.dumps(
                {
                    "time": self._format_timestamp(record),
                    "levelname": record.levelname,
                    "message": f"JSON formatting error: {str(e)}",
                    "filename": (
                        os.path.basename(record.pathname)
                        if record.pathname
                        else "unknown"
                    ),
                    "lineno": str(record.lineno),
                    "funcName": getattr(record, "funcName", "unknown") or "unknown",
                }
            )
