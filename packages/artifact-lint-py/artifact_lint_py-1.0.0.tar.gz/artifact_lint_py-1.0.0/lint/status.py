from enum import Enum
from typing import Union

class LintStatus(Enum):
    """
    The LintStatus enum represents the status or severity of a lint rule's
    result after the rule is enforced against an artifact.
    """
    INFO = 0
    WARNING = 1
    ERROR = 2

    @staticmethod
    def try_from_name(
            name: str
        ) -> tuple[Union["LintStatus", None], str]:
        """
        Try to load a LintStatus from its name property serialized as a string

        Args:
            name (str): The name of the LintStatus enum

        Returns:
            LintStatus: The loaded LintStatus, or None if not loaded
            str: Error message if the LintStatus was not loaded successfully
        """
        try:
            return LintStatus[name], ""
        except KeyError:
            return None, f"Task status name does not exist: {name}"

    @staticmethod
    def try_from_value(
            value: int
        ) -> tuple[Union["LintStatus", None], str]:
        """
        Try to load a LintStatus from its value property serialized as an int

        Args:
        value (int): The value of the LintStatus enum

        Returns:
            LintStatus: The loaded LintStatus, or None if not loaded
            str: Error message if the LintStatus was not loaded successfully
        """
        try:
            return LintStatus(value), ""
        except ValueError:
            return None, f"Task status value out of range: {value}"
