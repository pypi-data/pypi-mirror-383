from lint.status import LintStatus

class LintResult:
    """
    The LintResult class represents the result of a lint rule after the rule
    has been enforced against an artifact. It includes a LintStatus indicating
    the severity of the result, and a message represented as a string.
    """
    def __init__(
            self,
            status: LintStatus=LintStatus.INFO,
            message: str=""
        ):
        """
        Constructor for the LintResult class

        Args:
            status (LintStatus): The status / severity of the lint result
            message (str): A message describing the lint result
        """
        self.status = status
        self.message = message

    def __str__(self) -> str:
        """
        Formats the lint result as a string

        Returns:
            str: The lint result as a string
        """
        return f"{str(self.status)}: {self.message}"
