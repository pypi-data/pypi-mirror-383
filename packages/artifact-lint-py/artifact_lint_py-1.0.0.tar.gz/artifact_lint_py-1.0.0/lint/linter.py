from lint.config import LinterConfig
from lint.result import LintResult
from lint.rule import LintRule, DEFAULT_LINT_RULE_CONFIG
from lint.typing import T
from typing import Generic

DEFAULT_LINTER_CONFIG = LinterConfig({})

class Linter(Generic[T]):
    """
    The Linter class applies potentially multiple lint rules against an
    artifact, returning the list of lint results for each enforced rule
    """
    def __init__(
            self,
            rules: list[LintRule[T]]
        ):
        """
        Constructor for the Linter class

        Args:
            rules (list): The lint rules enforced by the linter
        """
        self.rules = rules

    def lint(
            self,
            artifact: T,
            config: LinterConfig[T]=DEFAULT_LINTER_CONFIG,
            **kwargs
        ) -> list[LintResult]:
        """
        Applies the linter's lint rules against an artifact, returning the list
        of lint results for each enforced rule

        Args:
            artifact (T): The artifact to lint
            config (LinterConfig): The configuration for the linter
        
        Returns:
            list: The list of LintResults corresponding to each lint rule
        """
        results = []
        for rule in self.rules:
            rule_name = rule.name()
            if config.enabled(rule_name):
                results.append(
                    rule.lint(
                        artifact,
                        config.config.get(
                            rule_name,
                            DEFAULT_LINT_RULE_CONFIG
                        )
                    )
                )
            else:
                results.append(LintResult(message=f"{rule_name} disabled"))
        return results
