from lint.config import LintRuleConfig
from lint.result import LintResult
from lint.typing import T
from typing import Generic

DEFAULT_LINT_RULE_CONFIG = LintRuleConfig({"enabled": True})

class LintRule(Generic[T]):
    """
    The LintRule class represents a rule that can be enforced against an
    artifact. When enforced, it produces a LintResult which describes the
    outcome of enforcing the rule.
    """
    def name(self) -> str:
        """
        Returns the name of the lint rule

        Returns:
            str: The name of the lint rule
        """
        return type(self).__name__

    def lint(
            self,
            artifact: T,
            config: LintRuleConfig[T]=DEFAULT_LINT_RULE_CONFIG,
            **kwargs
        ) -> LintResult:
        """
        Enforces the lint rule against an artifact

        Args:
            artifact (T): An artifact to lint
            config (LintRuleConfig): The configuration for this lint rule
        
        Returns:
            LintResult: The lint result
        """
        return LintResult(message="Not yet implemented")
