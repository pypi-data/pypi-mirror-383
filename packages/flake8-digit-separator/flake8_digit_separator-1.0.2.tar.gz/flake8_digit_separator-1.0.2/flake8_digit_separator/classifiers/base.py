from abc import ABC, abstractmethod
from typing import TypeAlias

from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.fds_numbers import (
    BinaryNumber,
    ComplexNumber,
    FloatNumber,
    HexNumber,
    IntNumber,
    OctalNumber,
    ScientificNumber,
)

LowerTokenLikeStr: TypeAlias = str
FDSNumbersWithPrefixAlias: TypeAlias = OctalNumber | HexNumber | BinaryNumber
FDSNumbersUnsupportedAlias: TypeAlias = ScientificNumber | ComplexNumber
FDSNumbersAlias: TypeAlias = IntNumber | FloatNumber | FDSNumbersUnsupportedAlias | FDSNumbersWithPrefixAlias


class Classifier(ABC):
    """Abstract classifier class."""

    @property
    @abstractmethod
    def token(self) -> TokenLikeStr:
        """Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """

    @property
    @abstractmethod
    def token_lower(self) -> LowerTokenLikeStr:
        """Token string from `tokenize.TokenInfo` object in lower case.

        :return: Token like string in lower case.
        :rtype: LowerTokenLikeStr
        """

    @abstractmethod
    def classify(self) -> FDSNumbersAlias | None:
        """Determines what specific number the token refers to.

        :return: Object of a specific number.
        :rtype: FDSNumbersAlias | None
        """


class BaseClassifier(Classifier):
    """Base classifier class.

    Specific classifiers should be inherited from this class.
    """

    @property
    def token_lower(self) -> LowerTokenLikeStr:
        """Token string from `tokenize.TokenInfo` object in lower case.

        :return: Token like string in lower case.
        :rtype: LowerTokenLikeStr
        """
        return self.token.lower()
