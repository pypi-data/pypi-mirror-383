import ast
import tokenize
from argparse import Namespace
from collections.abc import Iterator

from flake8.options.manager import OptionManager

from flake8_digit_separator.__version__ import NAME, VERSION
from flake8_digit_separator.classifiers.registry import ClassifierRegistry
from flake8_digit_separator.error import Error
from flake8_digit_separator.fds_numbers.types import FDSNumbersAlias
from flake8_digit_separator.types import ErrorMessage
from flake8_digit_separator.validators.registry import ValidatorRegistry


class Checker:
    """Flake8 plugin checker for digit separator violations in numeric literals.

    This checker processes Python source code tokens to identify numeric literals
    and validates that they follow proper digit separator conventions. It classifies
    different types of numbers (integers, floats, binary, hex, octal, etc.) and
    applies appropriate validation rules to ensure consistent formatting.
    """

    name = NAME
    version = VERSION
    options = None

    def __init__(
        self,
        tree: ast.AST,  # noqa: ARG002
        file_tokens: list[tokenize.TokenInfo],
    ) -> None:
        self.file_tokens = file_tokens
        self.excluded_numbers: set[int] = getattr(self.__class__, 'excluded_numbers', set())

    def run(self) -> Iterator[ErrorMessage]:
        """Entry point and start of validation.

        1. Check that the token is a number.
        2. Classify the token.
        3. Validate the token.
        4. Display an error.

        :yield: FDS rule that was broken.
        :rtype: Iterator[ErrorMessage]
        """
        for token in self.file_tokens:
            if token.type == tokenize.NUMBER:
                error = self._process_number_token(token)
                if error:
                    yield error.as_tuple()

    @classmethod
    def add_options(cls, parser: OptionManager) -> None:
        """Add configuration options to the flake8 parser.

        :param parser: The flake8 option parser.
        """
        parser.add_option(
            '--fds-exclude',
            action='store',
            type=str,
            default='',
            parse_from_config=True,
            help='Comma-separated list of integer numbers to exclude from digit separator validation (e.g. 8080, 1024)',
        )

    @classmethod
    def parse_options(cls, options: Namespace) -> None:
        """Parse the configuration options.

        :param options: The parsed options from flake8.
        """
        cls.options = options
        if hasattr(options, 'fds_exclude') and options.fds_exclude:
            excluded_strs = [num.strip() for num in options.fds_exclude.split(',') if num.strip()]  # noqa: WPS221
            try:
                cls.excluded_numbers = {int(num) for num in excluded_strs}
            except ValueError:
                cls.excluded_numbers = set()
        else:
            cls.excluded_numbers = set()

    def _process_number_token(
        self,
        token: tokenize.TokenInfo,
    ) -> Error | None:
        number = self._classify(token)

        if number:
            if not number.is_supported:
                return None

            if self._should_exclude_number(number):
                return None

            validator = ValidatorRegistry.get_validator(number)
            if validator.validate():
                return None

            return Error(
                line=token.start[0],
                column=token.start[1],
                message=validator.error_message,
                object_type=type(self),
            )

        return None

    def _should_exclude_number(self, number: FDSNumbersAlias) -> bool:
        """Check if a number should be excluded from validation.

        :param number: The classified number object.
        :return: True if the number should be excluded, False otherwise.
        """
        is_exclude_number = False
        try:
            if hasattr(number, 'token'):
                numeric_value = int(number.token)
                is_exclude_number = numeric_value in self.excluded_numbers
        except (AttributeError, ValueError):
            is_exclude_number = False

        return is_exclude_number

    def _classify(self, token: tokenize.TokenInfo) -> FDSNumbersAlias | None:
        classifiers = ClassifierRegistry.get_ordered_classifiers()
        number = None
        for classifier in classifiers:
            number = classifier(token.string).classify()
            if number:
                break

        return number if number else None
