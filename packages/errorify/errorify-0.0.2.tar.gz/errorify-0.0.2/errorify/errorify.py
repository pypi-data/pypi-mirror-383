from __future__ import annotations

import os
import traceback
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union

SEPARATOR_TOP = "-------------------------------- Error Details --------------------------------"
SEPARATOR_BOTTOM = "-------------------------------------------------------------------------------"


def _basename(path: Optional[str]) -> Optional[str]:
    return os.path.basename(path) if path else None


def _timestamp(
    offset: Optional[Union[int, float]] = None,
    fmt: str = "%Y-%m-%d %H:%M:%S %z"
) -> str:
    """
    Returns the current timestamp formatted with the given offset and format.

    Parameters:
        offset (int | float | None): Timezone offset in hours (e.g. +6, -5.5, +3.5).
                                     If None, defaults to UTC.
        fmt (str): Datetime format (default = '%Y-%m-%d %H:%M:%S %z')

    Returns:
        str: Formatted timestamp string.
    """
    if offset is not None:
        tzinfo = timezone(timedelta(minutes=round(offset * 60)))
    else:
        tzinfo = timezone.utc

    return datetime.now(tzinfo).strftime(fmt)


def errorify(
    error: BaseException,
    tz_offset: Optional[Union[int, float]] = None,
    timestamp_format: str = "%Y-%m-%d %H:%M:%S %z"
) -> str:
    """
    Formats and retrieves details about a caught exception.

    Parameters:
        error (BaseException): The caught exception object.
        tz_offset (int | float | None): Optional Timezone offset in hours (e.g., +6, -5.5, +3.5).
                                        Defaults to UTC if None.
        timestamp_format (str): Optional datetime format string.
                                Defaults to '%Y-%m-%d %H:%M:%S %z'.

    Returns:
        str: Formatted string containing exception details.
    """
    if not isinstance(error, BaseException):
        raise TypeError("errorify() expects a BaseException instance from an 'except' block")

    tb_list = traceback.extract_tb(error.__traceback__) if error.__traceback__ else []

    if not tb_list:
        details: List[str] = [
            SEPARATOR_TOP,
            f"Timestamp: {_timestamp(tz_offset, timestamp_format)}",
            f"Exception Name: {error.__class__.__name__}",
            f"Exception Message: {str(error)}",
            "Exception File Path: None",
            "Exception File Name: None",
            "Exception File Line Number: None",
            "Error File Path: None",
            "Error File Name: None",
            "Error Function Name: None",
            "Error File Line Number: None",
            SEPARATOR_BOTTOM,
        ]
        return "\n".join(details)

    first = tb_list[0]
    last = tb_list[-1]

    exception_file_path = os.path.abspath(first.filename) if first.filename else None
    exception_file_name = _basename(exception_file_path)
    exception_line_no = first.lineno

    error_file_path = os.path.abspath(last.filename) if last.filename else None
    error_file_name = _basename(error_file_path)
    function_name = last.name
    error_line_no = last.lineno

    details: List[str] = [
        SEPARATOR_TOP,
        f"Timestamp: {_timestamp(tz_offset, timestamp_format)}",
        f"Exception Name: {error.__class__.__name__}",
        f"Exception Message: {str(error)}",
        f"Exception File Path: {exception_file_path}",
        f"Exception File Name: {exception_file_name}",
        f"Exception File Line Number: {exception_line_no}",
        f"Error File Path: {error_file_path}",
        f"Error File Name: {error_file_name}",
        f"Error Function Name: {function_name}",
        f"Error File Line Number: {error_line_no}",
    ]

    cause = getattr(error, "__cause__", None) or getattr(error, "__context__", None)
    if cause is not None:
        details.append(f"Caused By: {cause.__class__.__name__}: {cause}")

    details.append(SEPARATOR_BOTTOM)
    return "\n".join(details)
