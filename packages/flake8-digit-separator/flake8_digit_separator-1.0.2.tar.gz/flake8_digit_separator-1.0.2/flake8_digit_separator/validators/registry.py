from typing import ClassVar, final

from flake8_digit_separator.fds_numbers.fds_numbers import (
    BinaryNumber,
    FloatNumber,
    HexNumber,
    IntNumber,
    OctalNumber,
)
from flake8_digit_separator.fds_numbers.types import FDSNumbersAlias
from flake8_digit_separator.validators.types import ValidatorsAlias, ValidatorsMapping
from flake8_digit_separator.validators.validator_binary import BinaryValidator
from flake8_digit_separator.validators.validator_float import FloatValidator
from flake8_digit_separator.validators.validator_hex import HexValidator
from flake8_digit_separator.validators.validator_int import IntValidator
from flake8_digit_separator.validators.validator_octal import OctalValidator


@final
class ValidatorRegistry:
    """Validator registrar.

    Matches validators and numbers.
    """

    mapping: ClassVar[ValidatorsMapping] = {
        IntNumber: IntValidator,
        HexNumber: HexValidator,
        OctalNumber: OctalValidator,
        BinaryNumber: BinaryValidator,
        FloatNumber: FloatValidator,
    }

    @classmethod
    def get_validator(cls, number: FDSNumbersAlias) -> ValidatorsAlias:
        """Returns the required validator by number.

        :param number: FDS number object received from the classifier.
        :type number: FDSNumbersAlias

        :raises ValueError: The required validator was not found.

        :return: Required validator.
        :rtype: ValidatorsAlias
        """
        validator_cls: type[ValidatorsAlias] | None = cls.mapping.get(number.__class__)
        if not validator_cls:
            msg = 'No validator registered for {number}'
            raise ValueError(
                msg.format(
                    number=number.__class__,
                ),
            )

        return validator_cls(number)  # type: ignore [arg-type]
