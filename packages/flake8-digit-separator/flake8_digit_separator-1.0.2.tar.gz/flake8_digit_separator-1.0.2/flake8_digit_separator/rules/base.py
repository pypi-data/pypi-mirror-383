import enum
from typing import TypeAlias

NumberWithSeparators: TypeAlias = str


class FDSRules(enum.Enum):
    """Flake8-digits-separator rules.

    When initializing an object, you must specify the rule number as the argument name.
    The rule text and a valid example must be specified as the argument value.
    """

    def __init__(
        self,
        text: str,
        example: NumberWithSeparators,
    ) -> None:
        self._text = text
        self._example = example

    def create_message(self) -> str:
        """Create a formatted error message for this rule.

        Combines the rule name, descriptive text, and example into a
        standardized error message format.

        :return: Formatted error message in the format
                 "{rule}: {text} (e.g. {example})"
        :rtype: str
        """
        msg = '{rule}: {text} (e.g. {example})'

        return msg.format(
            rule=self.name,
            text=self.text,
            example=self.example,
        )

    @property
    def text(self) -> str:
        """Text of rule."""
        return self._text

    @property
    def example(self) -> NumberWithSeparators:
        """Valid example of rule."""
        return self._example
