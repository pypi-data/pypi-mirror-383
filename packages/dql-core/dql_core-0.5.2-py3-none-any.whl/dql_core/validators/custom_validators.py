"""Validators for custom validation logic.

Implements validator for custom lambda expressions with security restrictions.

[Source: Story 2.1 - Advanced Operators Support]
"""

from typing import Any, Iterable
import ast
import operator

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


# Safe built-in functions allowed in lambda expressions
SAFE_BUILTINS = {
    'abs': abs,
    'all': all,
    'any': any,
    'bool': bool,
    'dict': dict,
    'float': float,
    'int': int,
    'len': len,
    'list': list,
    'max': max,
    'min': min,
    'round': round,
    'set': set,
    'sorted': sorted,
    'str': str,
    'sum': sum,
    'tuple': tuple,
}

# Safe operators allowed in lambda expressions
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
    ast.BitOr: operator.or_,
    ast.BitXor: operator.xor,
    ast.BitAnd: operator.and_,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.And: lambda a, b: a and b,
    ast.Or: lambda a, b: a or b,
    ast.Not: operator.not_,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Invert: operator.inv,
}


class ToSatisfyValidator(Validator):
    """Validator for to_satisfy operator.

    Validates that field values satisfy a custom lambda expression.
    Implements security restrictions to prevent malicious code execution.

    Security Restrictions:
    - No imports allowed (__import__, import statements)
    - No file I/O operations
    - No exec/eval/compile
    - Limited to safe built-in functions
    - No attribute access on dangerous objects

    Example:
        expect column("age") to_satisfy("lambda x: x > 18 and x < 100") severity critical
        expect column("name") to_satisfy("lambda x: len(x) > 2 and x.startswith('A')") severity warning
    """

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values satisfy custom lambda expression.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToSatisfy operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status

        Raises:
            ValidationError: If operator, target, or lambda expression is invalid
        """
        from dql_parser.ast_nodes import ColumnTarget, ToSatisfy

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_satisfy only works with column targets")

        if not isinstance(expectation.operator, ToSatisfy):
            raise ValidationError("Expected ToSatisfy operator")

        field_name = expectation.target.field_name
        lambda_expr = expectation.operator.expression

        # Parse and validate the lambda expression
        try:
            lambda_func = self._parse_lambda(lambda_expr)
        except (SyntaxError, ValueError) as e:
            raise ValidationError(f"Invalid lambda expression '{lambda_expr}': {e}")

        total = 0
        failed = 0
        failures = []

        for record in records:
            total += 1
            value = executor.get_field_value(record, field_name)

            # Note: Unlike other validators, we don't automatically skip nulls
            # The lambda expression can decide how to handle them
            try:
                result = lambda_func(value)
                if not result:
                    failed += 1
                    failures.append(
                        {
                            "record": str(record),
                            "field": field_name,
                            "value": value,
                            "expression": lambda_expr,
                            "reason": f"Value {repr(value)} does not satisfy lambda: {lambda_expr}",
                        }
                    )
            except Exception as e:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "expression": lambda_expr,
                        "reason": f"Error evaluating lambda on value {repr(value)}: {type(e).__name__}: {e}",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )

    def _parse_lambda(self, lambda_expr: str):
        """Parse and compile lambda expression with security checks.

        Args:
            lambda_expr: Lambda expression string (e.g., "lambda x: x > 10")

        Returns:
            Compiled lambda function

        Raises:
            SyntaxError: If lambda expression has syntax errors
            ValueError: If lambda expression violates security restrictions
        """
        # Parse the expression
        try:
            tree = ast.parse(lambda_expr, mode='eval')
        except SyntaxError as e:
            raise SyntaxError(f"Invalid syntax: {e}")

        # Security check: validate AST structure
        self._validate_ast_security(tree)

        # Compile with restricted globals
        code = compile(tree, '<lambda>', 'eval')

        # Create restricted namespace with only safe builtins
        safe_globals = {
            '__builtins__': SAFE_BUILTINS,
        }

        # Evaluate to get the lambda function
        try:
            lambda_func = eval(code, safe_globals)
        except Exception as e:
            raise ValueError(f"Failed to evaluate lambda: {e}")

        # Verify it's actually a lambda/function
        if not callable(lambda_func):
            raise ValueError(f"Expression did not produce a callable: {lambda_expr}")

        return lambda_func

    def _validate_ast_security(self, tree: ast.AST):
        """Validate AST structure for security violations.

        Args:
            tree: Parsed AST tree

        Raises:
            ValueError: If AST contains dangerous operations
        """
        for node in ast.walk(tree):
            # Block import statements
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise ValueError("Import statements are not allowed for security reasons")

            # Block dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    dangerous_funcs = {
                        '__import__', 'eval', 'exec', 'compile',
                        'open', 'input', 'file', 'execfile',
                        'globals', 'locals', 'vars', 'dir',
                        'getattr', 'setattr', 'delattr', 'hasattr',
                    }
                    if func_name in dangerous_funcs:
                        raise ValueError(
                            f"Function '{func_name}' is not allowed for security reasons"
                        )

            # Block attribute access to dangerous attributes
            if isinstance(node, ast.Attribute):
                dangerous_attrs = {
                    '__import__', '__builtins__', '__globals__',
                    '__code__', '__closure__', '__dict__',
                }
                if node.attr in dangerous_attrs:
                    raise ValueError(
                        f"Attribute '{node.attr}' access is not allowed for security reasons"
                    )

            # Block list/dict comprehensions (could be used for side effects)
            # Note: This is overly restrictive but safer
            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                raise ValueError("Comprehensions are not allowed for security reasons")
