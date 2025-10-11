from jsonschema import validate, ValidationError
from lint.typing import T
from typing import Generic, Any

DEFAULT_LINT_RULE_CONFIG_SCHEMA = {
    "type": "object",
    "required": [ "enabled" ],
    "properties": {
        "enabled": {
            "type": "boolean"
        }
    }
}
"""
The default lint rule config schema, which enforces that lint rule config
dicts have a boolean property named enabled
"""

DEFAULT_LINTER_CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "patternProperties": {
        "^[A-Z][a-zA-Z0-9]*$": DEFAULT_LINT_RULE_CONFIG_SCHEMA
    }
}
"""
The default schema for a linter config, which enforces that lint rule names
are PascalCase and that each lint rule config satisfies its default schema
"""

class LintRuleConfig(Generic[T]):
    """
    The LintRuleConfig class represents the configuration for a lint rule
    """
    @staticmethod
    def validate_static(
            config: dict[str, Any],
            schema: dict[str, Any]=DEFAULT_LINT_RULE_CONFIG_SCHEMA
        ) -> tuple[bool, str]:
        """
        Validates a LintRuleConfig dictionary

        Args:
            config (dict): The lint rule config dictionary
            schema (dict): The lint rule config dictionary
        
        Returns:
            bool: Whether the lint rule config dict was valid
            str: Error message if the config dict was invalid
        """
        try:
            validate(schema=schema, instance=config)
        except ValidationError as ve:
            return False, str(ve)
        return True, ""

    def __init__(
            self,
            config: dict[str, Any],
            schema: dict[str, Any]=DEFAULT_LINT_RULE_CONFIG_SCHEMA
        ):
        """
        Constructor for the LintRuleConfig class

        Args:
            config (dict): The lint rule config dictionary
            schema (dict): The lint rule config JSON schema dictionary
        
        Returns:
            LintRuleConfig: The initialized lint rule config object
        """
        # Validate the lint rule config
        valid, err = LintRuleConfig.validate_static(config, schema)
        if not valid:
            raise ValidationError(err)
        
        # If valid, save the config & schema as object properties
        self.config = config
        self.schema = schema

    def validate(self) -> tuple[bool, str]:
        """
        Validates a LintRuleConfig instance
        
        Returns:
            bool: Whether the config dict was valid
            str: Error message if the config dict was invalid
        """
        return LintRuleConfig.validate_static(self.config, self.schema)

    def enabled(self) -> bool:
        """
        Determines whether the lint rule is enabled
        
        Returns:
            bool: Whether the lint rule is enabled
        """
        return self.config.get("enabled", False)
    
    def __dict__(self) -> dict[str, Any]:
        """
        Serialize the LintRuleConfig as a python dictionary

        Returns:
            dict: The lint rule config as a dict
        """
        return self.config

class LinterConfig(Generic[T]):
    """
    The LinterConfig class represents the configuration for a linter
    """
    @staticmethod
    def validate_static(
            config: dict[str, Any],
            schema: dict[str, Any]=DEFAULT_LINTER_CONFIG_SCHEMA
        ) -> tuple[bool, str]:
        """
        Validates a LinterConfig dictionary

        Args:
            config (dict): The linter config dictionary
            schema (dict): The linter config JSON schema dictionary
        
        Returns:
            bool: Whether the config dict was valid
            str: Error message if the config dict was invalid
        """
        try:
            validate(schema=schema, instance=config)
        except ValidationError as ve:
            return False, str(ve)
        return True, ""

    def __init__(
            self,
            config: dict[str, Any],
            schema: dict[str, Any]=DEFAULT_LINTER_CONFIG_SCHEMA
        ):
        """
        Constructor for the LinterConfig class

        Args:
            config (dict): The linter config dictionary
            schema (dict): The linter config JSON schema dictionary
        """
        # Validate the linter config
        valid, err = LinterConfig.validate_static(config, schema)
        if not valid:
            raise ValidationError(err)
        
        # If valid, save the config & schema as object properties
        # Convert each lint rule config to a LintRuleConfig before saving
        self.config = { 
            key: LintRuleConfig(value) for key, value in config.items()
        }
        self.schema = schema

    def validate(self) -> tuple[bool, str]:
        """
        Validates a LinterConfig instance
        
        Returns:
            bool: Whether the config dict was valid
            str: Error message if the config dict was invalid
        """
        return LinterConfig.validate_static(self.__dict__(), self.schema)

    def enabled(self, rule: str) -> bool:
        """
        Determines whether a given lint rule is enabled in the lint config

        Args:
            rule (str): The name of the lint rule
        
        Returns:
            bool: Whether the lint rule is enabled
        """
        for key in self.config.keys():
            if rule == str(key):
                return self.config.get(key).enabled()
        return False

    def __dict__(self) -> dict[str, Any]:
        """
        Serialize the LinterConfig as a python dictionary

        Returns:
            dict: The linter config serialized as a dict
        """
        return {
            key: value.__dict__() for key, value in self.config.items()
        }
