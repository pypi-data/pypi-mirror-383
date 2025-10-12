import enum


@enum.unique
class NumeralSystem(enum.Enum):
    """Supported number systems."""

    BINARY = 2
    OCTAL = 8
    FLOAT = 10
    HEX = 16


@enum.unique
class NumberPrefix(enum.Enum):
    """Supported number prefix."""

    BINARY = '0b_'
    OCTAL = '0o_'
    HEX = '0x_'

    def get_value_without_separator(self) -> str:
        """Get the number prefix without the trailing underscore separator.

        Removes the last character (underscore) from the prefix value to get
        the clean prefix format (e.g. '0b_' becomes '0b').

        :return: Number prefix without the trailing underscore
        :rtype: str
        """
        return self.value[:-1]


@enum.unique
class NumberDelimiter(enum.Enum):
    """Supported number delimiters."""

    FLOAT = '.'
