"""Expression evaluator for computed columns.

This module provides runtime evaluation of DQL expressions including:
- String functions (CONCAT, UPPER, LOWER, TRIM, LENGTH)
- Date functions (YEAR, MONTH, DAY, AGE)
- Arithmetic operations (+, -, *, /, %)
- NULL propagation (SQL-style)
"""

from typing import Any, Dict, Callable
from datetime import date, datetime
from decimal import Decimal


class ExpressionEvaluator:
    """Evaluates DQL expression nodes at runtime.

    Handles NULL propagation, type coercion, and error handling
    for all supported expression types.
    """

    def __init__(self):
        """Initialize evaluator with function registry."""
        self._functions: Dict[str, Callable] = {
            # String functions
            "CONCAT": self._concat,
            "UPPER": self._upper,
            "LOWER": self._lower,
            "TRIM": self._trim,
            "LENGTH": self._length,
            # Date functions
            "YEAR": self._year,
            "MONTH": self._month,
            "DAY": self._day,
            "AGE": self._age,
        }

    def evaluate(self, expr_node: Any, record: Any, executor: Any = None) -> Any:
        """Evaluate expression node against a record.

        Args:
            expr_node: AST node (Value, FieldRef, ArithmeticExpr, FunctionCall, etc.)
            record: Record object to evaluate against
            executor: Optional ValidationExecutor for field access

        Returns:
            Evaluated value (can be None for NULL)

        Raises:
            ValueError: For type errors, invalid operations, etc.
        """
        from dql_parser.ast_nodes import (
            Value,
            FieldRef,
            ColumnRef,
            ArithmeticExpr,
            FunctionCall,
            ExprTarget,
        )

        # Handle Value nodes (literals)
        if isinstance(expr_node, Value):
            return expr_node.value

        # Handle FieldRef nodes (field access)
        if isinstance(expr_node, FieldRef):
            if executor is None:
                raise ValueError("Executor required for field access")
            return executor.get_field_value(record, expr_node.field_name)

        # Handle ColumnRef nodes (column access - alias for FieldRef)
        if isinstance(expr_node, ColumnRef):
            if executor is None:
                raise ValueError("Executor required for column access")
            return executor.get_field_value(record, expr_node.field_name)

        # Handle ArithmeticExpr nodes
        if isinstance(expr_node, ArithmeticExpr):
            return self._evaluate_arithmetic(expr_node, record, executor)

        # Handle FunctionCall nodes
        if isinstance(expr_node, FunctionCall):
            return self._evaluate_function(expr_node, record, executor)

        # Handle ExprTarget (shouldn't happen in recursive evaluation)
        if isinstance(expr_node, ExprTarget):
            return self.evaluate(expr_node.expression, record, executor)

        raise ValueError(f"Unsupported expression node type: {type(expr_node).__name__}")

    def _evaluate_arithmetic(self, expr: Any, record: Any, executor: Any) -> Any:
        """Evaluate arithmetic expression with NULL propagation.

        Args:
            expr: ArithmeticExpr node
            record: Record to evaluate against
            executor: ValidationExecutor for field access

        Returns:
            Numeric result or None (NULL propagation)

        Raises:
            ValueError: For type errors, division by zero, etc.
        """
        # Evaluate operands
        left_val = self.evaluate(expr.left, record, executor)
        right_val = self.evaluate(expr.right, record, executor)

        # NULL propagation
        if left_val is None or right_val is None:
            return None

        # Type coercion to numeric
        try:
            left_num = self._to_number(left_val)
            right_num = self._to_number(right_val)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot perform arithmetic on non-numeric values: {e}")

        # Perform operation
        op = expr.operator
        if op == "+":
            return left_num + right_num
        elif op == "-":
            return left_num - right_num
        elif op == "*":
            return left_num * right_num
        elif op == "/":
            if right_num == 0:
                raise ValueError("Division by zero")
            # Preserve integer division if both are ints
            if isinstance(left_num, int) and isinstance(right_num, int):
                return left_num // right_num
            return left_num / right_num
        elif op == "%":
            if right_num == 0:
                raise ValueError("Modulo by zero")
            return left_num % right_num
        else:
            raise ValueError(f"Unsupported arithmetic operator: {op}")

    def _evaluate_function(self, func: Any, record: Any, executor: Any) -> Any:
        """Evaluate function call with NULL propagation.

        Args:
            func: FunctionCall node
            record: Record to evaluate against
            executor: ValidationExecutor for field access

        Returns:
            Function result or None (NULL propagation)

        Raises:
            ValueError: For unknown functions or invalid arguments
        """
        func_name = func.function_name.upper()

        if func_name not in self._functions:
            raise ValueError(f"Unknown function: {func_name}")

        # Evaluate arguments
        args = [self.evaluate(arg, record, executor) for arg in func.args]

        # Call function handler
        handler = self._functions[func_name]
        return handler(*args)

    # ==================== String Functions ====================

    def _concat(self, *args: Any) -> Any:
        """CONCAT function - concatenate strings with NULL propagation.

        Returns None if any argument is None.
        """
        if any(arg is None for arg in args):
            return None

        return "".join(str(arg) for arg in args)

    def _upper(self, value: Any) -> Any:
        """UPPER function - convert to uppercase with NULL propagation."""
        if value is None:
            return None
        return str(value).upper()

    def _lower(self, value: Any) -> Any:
        """LOWER function - convert to lowercase with NULL propagation."""
        if value is None:
            return None
        return str(value).lower()

    def _trim(self, value: Any) -> Any:
        """TRIM function - remove leading/trailing whitespace with NULL propagation."""
        if value is None:
            return None
        return str(value).strip()

    def _length(self, value: Any) -> Any:
        """LENGTH function - string length with NULL propagation."""
        if value is None:
            return None
        return len(str(value))

    # ==================== Date Functions ====================

    def _year(self, value: Any) -> Any:
        """YEAR function - extract year from date with NULL propagation."""
        if value is None:
            return None

        if isinstance(value, (date, datetime)):
            return value.year

        raise ValueError(f"YEAR requires date/datetime value, got {type(value).__name__}")

    def _month(self, value: Any) -> Any:
        """MONTH function - extract month from date with NULL propagation."""
        if value is None:
            return None

        if isinstance(value, (date, datetime)):
            return value.month

        raise ValueError(f"MONTH requires date/datetime value, got {type(value).__name__}")

    def _day(self, value: Any) -> Any:
        """DAY function - extract day from date with NULL propagation."""
        if value is None:
            return None

        if isinstance(value, (date, datetime)):
            return value.day

        raise ValueError(f"DAY requires date/datetime value, got {type(value).__name__}")

    def _age(self, value: Any, reference: Any = None) -> Any:
        """AGE function - calculate age in years from date with NULL propagation.

        Args:
            value: Birth date
            reference: Reference date (defaults to today)

        Returns:
            Age in years as integer
        """
        if value is None:
            return None

        if not isinstance(value, (date, datetime)):
            raise ValueError(f"AGE requires date/datetime value, got {type(value).__name__}")

        # Default reference to today
        if reference is None:
            reference = date.today()
        elif isinstance(reference, datetime):
            reference = reference.date()
        elif not isinstance(reference, date):
            raise ValueError(f"AGE reference must be date/datetime, got {type(reference).__name__}")

        # Calculate age
        age = reference.year - value.year

        # Adjust if birthday hasn't occurred yet this year
        if isinstance(value, datetime):
            value = value.date()

        if (reference.month, reference.day) < (value.month, value.day):
            age -= 1

        return age

    # ==================== Helper Methods ====================

    def _to_number(self, value: Any) -> Any:
        """Convert value to numeric type (int, float, Decimal).

        Args:
            value: Value to convert

        Returns:
            Numeric value

        Raises:
            ValueError: If value cannot be converted to number
        """
        # Already numeric
        if isinstance(value, (int, float, Decimal)):
            return value

        # Try converting string to number
        if isinstance(value, str):
            # Try int first
            try:
                return int(value)
            except ValueError:
                pass

            # Try float
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to number")

        raise ValueError(f"Cannot convert {type(value).__name__} to number")
