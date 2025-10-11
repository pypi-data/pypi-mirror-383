![artifact-lint-py](https://raw.githubusercontent.com/whatsacomputertho/artifact-lint-py/main/doc/source/_static/artifact-lint-py.png)

# artifact-lint-py

[![Test](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/test.yaml/badge.svg)](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/test.yaml) [![Sec](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/sec.yaml/badge.svg)](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/sec.yaml) [![Doc](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/doc.yaml/badge.svg)](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/doc.yaml) [![Build](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/build.yaml/badge.svg)](https://github.com/whatsacomputertho/artifact-lint-py/actions/workflows/build.yaml)

A python framework for developing artifact linters

**Docs**: https://whatsacomputertho.github.io/artifact-lint-py/

**Contributing**: [CONTRIBUTING.md](https://github.com/whatsacomputertho/artifact-lint-py/blob/main/CONTRIBUTING.md)

## Quick Example

```python
from lint.rule import LintRule
from lint.result import LintResult
from lint.status import LintStatus

class IntegerIsEven(LintRule[int]):
    def lint(self, artifact: int) -> LintResult:
        if artifact % 2 == 0:
            return LintResult(
                status=LintStatus.INFO,
                message=f"({self.name()}) Integer was even: {artifact}"
            )
        return LintResult(
            status=LintStatus.ERROR,
            message=f"({self.name()}) Integer was odd: {artifact}"
        )
integer_is_even = IntegerIsEven()

# Lint an even integer
even_result = integer_is_even.lint(2)
print(even_result)

# Lint an odd integer
odd_result = integer_is_even.lint(337)
print(odd_result)
```

To run this example, simply execute the following from the root of this repository
```bash
python3 examples/quick-example.py
```

## Installation

### Using Pip

Run the following command to install the latest version of this package
```bash
pip install artifact-lint-py
```

### Local Install

1. Clone this repository
2. [Build the project from source](#build)
3. Locate the `.whl` (wheel) file in the `dist` folder
    - It should be named something like so: artifact_lint_py-1.0.0-py3-none-any.whl
4. Run the following command from the root of the repository, replacing the name of the `.whl` file if necessary
    ```bash
    pip install dist/artifact_lint_py-1.0.0-py3-none-any.whl
    ```

## Build

From the root of this repository, execute
```bash
make build
```

Under the hood, this will execute python3 -m build and produce a .whl (wheel) and .tgz (TAR-GZip archive) file in the dist subdirectory. For more on this project's make recipes, see [CONTRIBUTING.md](CONTRIBUTING.md).
