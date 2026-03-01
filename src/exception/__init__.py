# src/exception/__init__.py

import os
import sys
import traceback


def error_message_detail(error: Exception, error_detail=sys) -> str:
    """
    Extract detailed error message with file name and line number
    """
    try:
        exc_type, exc_obj, exc_tb = error_detail.exc_info()

        if exc_tb is None:
            return str(error)

        file_name = os.path.basename(exc_tb.tb_frame.f_code.co_filename)
        line_number = exc_tb.tb_lineno

        return (
            f"Error occurred in python script [{file_name}] "
            f"at line number [{line_number}] "
            f"with error message [{error}]"
        )

    except Exception:
        # Absolute fallback (never crash error handling)
        return str(error)


class VisibilityException(Exception):
    """
    Custom exception for Climate Visibility project
    """

    def __init__(self, error: Exception, error_detail=sys):
        super().__init__(str(error))
        self.error_message = error_message_detail(error, error_detail)

    def __str__(self):
        return self.error_message
