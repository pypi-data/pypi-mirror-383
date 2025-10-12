from dataclasses import astuple, dataclass

from flake8_digit_separator.types import ErrorMessage


@dataclass(frozen=True)
class Error:
    """FDS rule violation with location."""

    line: int
    column: int
    message: str
    object_type: type[object]

    def as_tuple(self) -> ErrorMessage:
        """Convert the Error object to a tuple format expected by flake8.

        :return: A tuple containing (line, column, message, object_type) that
                 flake8 can process as an error report.
        :rtype: ErrorMessage
        """
        return astuple(self)
