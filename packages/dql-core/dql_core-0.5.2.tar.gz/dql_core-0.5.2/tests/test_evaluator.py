"""Unit tests for ExpressionEvaluator (Story 2.3)."""

import pytest
from datetime import date, datetime
from decimal import Decimal

from dql_core.evaluator import ExpressionEvaluator
from dql_parser.ast_nodes import (
    Value,
    FieldRef,
    ColumnRef,
    ArithmeticExpr,
    FunctionCall,
    ExprTarget,
)
from tests.conftest import MockRecord, MockExecutor


# ==================== String Function Tests ====================


class TestStringFunctions:
    """Test string function evaluation."""

    def test_concat_basic(self, mock_executor):
        """Test CONCAT with multiple string arguments."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(first="John", last="Doe")

        expr = FunctionCall(
            function_name="CONCAT",
            args=[
                FieldRef(field_name="first"),
                Value(value=" "),
                FieldRef(field_name="last"),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "John Doe"

    def test_concat_null_propagation(self, mock_executor):
        """Test CONCAT returns None if any argument is None."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(first="John", last=None)

        expr = FunctionCall(
            function_name="CONCAT",
            args=[
                FieldRef(field_name="first"),
                Value(value=" "),
                FieldRef(field_name="last"),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_concat_empty_strings(self, mock_executor):
        """Test CONCAT with empty strings."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a="", b="", c="")

        expr = FunctionCall(
            function_name="CONCAT",
            args=[
                FieldRef(field_name="a"),
                FieldRef(field_name="b"),
                FieldRef(field_name="c"),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == ""

    def test_concat_numeric_values(self, mock_executor):
        """Test CONCAT coerces numeric values to strings."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(id=123, name="User")

        expr = FunctionCall(
            function_name="CONCAT",
            args=[
                Value(value="ID:"),
                FieldRef(field_name="id"),
                Value(value="-"),
                FieldRef(field_name="name"),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "ID:123-User"

    def test_upper_basic(self, mock_executor):
        """Test UPPER converts to uppercase."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="john doe")

        expr = FunctionCall(function_name="UPPER", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "JOHN DOE"

    def test_upper_null_propagation(self, mock_executor):
        """Test UPPER returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name=None)

        expr = FunctionCall(function_name="UPPER", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_lower_basic(self, mock_executor):
        """Test LOWER converts to lowercase."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="JOHN DOE")

        expr = FunctionCall(function_name="LOWER", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "john doe"

    def test_lower_null_propagation(self, mock_executor):
        """Test LOWER returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name=None)

        expr = FunctionCall(function_name="LOWER", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_trim_basic(self, mock_executor):
        """Test TRIM removes leading/trailing whitespace."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="  John Doe  ")

        expr = FunctionCall(function_name="TRIM", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "John Doe"

    def test_trim_null_propagation(self, mock_executor):
        """Test TRIM returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name=None)

        expr = FunctionCall(function_name="TRIM", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_trim_no_whitespace(self, mock_executor):
        """Test TRIM with no whitespace."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="JohnDoe")

        expr = FunctionCall(function_name="TRIM", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "JohnDoe"

    def test_length_basic(self, mock_executor):
        """Test LENGTH returns string length."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="John")

        expr = FunctionCall(function_name="LENGTH", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 4

    def test_length_null_propagation(self, mock_executor):
        """Test LENGTH returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name=None)

        expr = FunctionCall(function_name="LENGTH", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_length_empty_string(self, mock_executor):
        """Test LENGTH with empty string."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="")

        expr = FunctionCall(function_name="LENGTH", args=[FieldRef(field_name="name")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 0


# ==================== Date Function Tests ====================


class TestDateFunctions:
    """Test date function evaluation."""

    def test_year_basic(self, mock_executor):
        """Test YEAR extracts year from date."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=date(1990, 5, 15))

        expr = FunctionCall(function_name="YEAR", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 1990

    def test_year_datetime(self, mock_executor):
        """Test YEAR works with datetime."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(created_at=datetime(2023, 12, 25, 10, 30, 0))

        expr = FunctionCall(function_name="YEAR", args=[FieldRef(field_name="created_at")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 2023

    def test_year_null_propagation(self, mock_executor):
        """Test YEAR returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=None)

        expr = FunctionCall(function_name="YEAR", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_year_invalid_type(self, mock_executor):
        """Test YEAR raises error for non-date value."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date="1990-05-15")

        expr = FunctionCall(function_name="YEAR", args=[FieldRef(field_name="birth_date")])

        with pytest.raises(ValueError, match="YEAR requires date/datetime"):
            evaluator.evaluate(expr, record, mock_executor)

    def test_month_basic(self, mock_executor):
        """Test MONTH extracts month from date."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=date(1990, 5, 15))

        expr = FunctionCall(function_name="MONTH", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 5

    def test_month_null_propagation(self, mock_executor):
        """Test MONTH returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=None)

        expr = FunctionCall(function_name="MONTH", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_day_basic(self, mock_executor):
        """Test DAY extracts day from date."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=date(1990, 5, 15))

        expr = FunctionCall(function_name="DAY", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 15

    def test_day_null_propagation(self, mock_executor):
        """Test DAY returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=None)

        expr = FunctionCall(function_name="DAY", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_age_basic(self, mock_executor):
        """Test AGE calculates age from birth date."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=date(1990, 5, 15))

        # Reference date: 2025-10-10
        expr = FunctionCall(
            function_name="AGE",
            args=[
                FieldRef(field_name="birth_date"),
                Value(value=date(2025, 10, 10)),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 35  # 2025 - 1990 = 35

    def test_age_birthday_not_yet(self, mock_executor):
        """Test AGE adjusts when birthday hasn't occurred yet."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=date(1990, 12, 25))

        # Reference date: 2025-10-10 (before birthday)
        expr = FunctionCall(
            function_name="AGE",
            args=[
                FieldRef(field_name="birth_date"),
                Value(value=date(2025, 10, 10)),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 34  # Birthday not yet, so 34 not 35

    def test_age_default_today(self, mock_executor):
        """Test AGE defaults to today if no reference date."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=date(1990, 1, 1))

        expr = FunctionCall(function_name="AGE", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        # Should be around 35 years (as of 2025-10-10 in test env)
        assert isinstance(result, int)
        assert result >= 35

    def test_age_null_propagation(self, mock_executor):
        """Test AGE returns None for None input."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=None)

        expr = FunctionCall(function_name="AGE", args=[FieldRef(field_name="birth_date")])

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_age_datetime_support(self, mock_executor):
        """Test AGE works with datetime objects."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=datetime(1990, 5, 15, 10, 30, 0))

        expr = FunctionCall(
            function_name="AGE",
            args=[
                FieldRef(field_name="birth_date"),
                Value(value=datetime(2025, 10, 10, 15, 45, 0)),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 35


# ==================== Arithmetic Operator Tests ====================


class TestArithmeticOperators:
    """Test arithmetic operator evaluation."""

    def test_addition_integers(self, mock_executor):
        """Test addition with integers."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=10, b=20)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 30

    def test_subtraction_integers(self, mock_executor):
        """Test subtraction with integers."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=50, b=20)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="-",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 30

    def test_multiplication_integers(self, mock_executor):
        """Test multiplication with integers."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=6, b=7)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="*",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 42

    def test_division_integers(self, mock_executor):
        """Test integer division with integers."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=20, b=4)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="/",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 5  # Integer division

    def test_division_floats(self, mock_executor):
        """Test division with floats."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=10.0, b=3.0)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="/",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert abs(result - 3.333333) < 0.001

    def test_division_by_zero(self, mock_executor):
        """Test division by zero raises error."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=10, b=0)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="/",
            right=FieldRef(field_name="b"),
        )

        with pytest.raises(ValueError, match="Division by zero"):
            evaluator.evaluate(expr, record, mock_executor)

    def test_modulo_basic(self, mock_executor):
        """Test modulo operator."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=17, b=5)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="%",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 2

    def test_modulo_by_zero(self, mock_executor):
        """Test modulo by zero raises error."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=10, b=0)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="%",
            right=FieldRef(field_name="b"),
        )

        with pytest.raises(ValueError, match="Modulo by zero"):
            evaluator.evaluate(expr, record, mock_executor)

    def test_arithmetic_null_propagation_left(self, mock_executor):
        """Test arithmetic returns None if left operand is None."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=None, b=10)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_arithmetic_null_propagation_right(self, mock_executor):
        """Test arithmetic returns None if right operand is None."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=10, b=None)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result is None

    def test_arithmetic_mixed_int_float(self, mock_executor):
        """Test arithmetic with mixed int/float operands."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=10, b=3.5)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 13.5

    def test_arithmetic_decimal_support(self, mock_executor):
        """Test arithmetic with Decimal values."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=Decimal("10.50"), b=Decimal("2.25"))

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == Decimal("12.75")

    def test_arithmetic_string_coercion(self, mock_executor):
        """Test arithmetic with string numbers."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a="10", b="5")

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 15

    def test_arithmetic_invalid_type(self, mock_executor):
        """Test arithmetic with non-numeric value raises error."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a="abc", b=10)

        expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )

        with pytest.raises(ValueError, match="Cannot perform arithmetic on non-numeric"):
            evaluator.evaluate(expr, record, mock_executor)

    def test_nested_arithmetic(self, mock_executor):
        """Test nested arithmetic expressions (a + b) * c."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=2, b=3, c=4)

        # (a + b) * c
        inner = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )
        outer = ArithmeticExpr(
            left=inner,
            operator="*",
            right=FieldRef(field_name="c"),
        )

        result = evaluator.evaluate(outer, record, mock_executor)
        assert result == 20  # (2 + 3) * 4 = 20


# ==================== Core Evaluation Tests ====================


class TestCoreEvaluation:
    """Test core evaluation logic."""

    def test_value_literal(self, mock_executor):
        """Test evaluating Value node (literal)."""
        evaluator = ExpressionEvaluator()
        record = MockRecord()

        expr = Value(value=42)

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 42

    def test_field_ref(self, mock_executor):
        """Test evaluating FieldRef node."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="John")

        expr = FieldRef(field_name="name")

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "John"

    def test_column_ref(self, mock_executor):
        """Test evaluating ColumnRef node (alias for FieldRef)."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(email="test@example.com")

        expr = ColumnRef(field_name="email")

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "test@example.com"

    def test_field_ref_no_executor(self):
        """Test FieldRef without executor raises error."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="John")

        expr = FieldRef(field_name="name")

        with pytest.raises(ValueError, match="Executor required for field access"):
            evaluator.evaluate(expr, record, executor=None)

    def test_unknown_function(self, mock_executor):
        """Test unknown function raises error."""
        evaluator = ExpressionEvaluator()
        record = MockRecord()

        expr = FunctionCall(function_name="UNKNOWN_FUNC", args=[Value(value=42)])

        with pytest.raises(ValueError, match="Unknown function: UNKNOWN_FUNC"):
            evaluator.evaluate(expr, record, mock_executor)

    def test_unsupported_node_type(self, mock_executor):
        """Test unsupported node type raises error."""
        evaluator = ExpressionEvaluator()
        record = MockRecord()

        # Use a random object as an invalid node
        expr = {"invalid": "node"}

        with pytest.raises(ValueError, match="Unsupported expression node type"):
            evaluator.evaluate(expr, record, mock_executor)

    def test_expr_target_unwrapping(self, mock_executor):
        """Test ExprTarget unwraps to inner expression."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=10, b=20)

        inner_expr = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )
        expr = ExprTarget(expression=inner_expr)

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 30


# ==================== Complex Expression Tests ====================


class TestComplexExpressions:
    """Test complex nested expressions."""

    def test_concat_with_upper(self, mock_executor):
        """Test CONCAT(UPPER(first), ' ', UPPER(last))."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(first="john", last="doe")

        expr = FunctionCall(
            function_name="CONCAT",
            args=[
                FunctionCall(function_name="UPPER", args=[FieldRef(field_name="first")]),
                Value(value=" "),
                FunctionCall(function_name="UPPER", args=[FieldRef(field_name="last")]),
            ],
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == "JOHN DOE"

    def test_arithmetic_with_function(self, mock_executor):
        """Test LENGTH(name) * 2."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(name="John")

        expr = ArithmeticExpr(
            left=FunctionCall(function_name="LENGTH", args=[FieldRef(field_name="name")]),
            operator="*",
            right=Value(value=2),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 8  # LENGTH("John") * 2 = 4 * 2 = 8

    def test_nested_arithmetic_with_functions(self, mock_executor):
        """Test (LENGTH(first) + LENGTH(last)) * 2."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(first="John", last="Doe")

        inner = ArithmeticExpr(
            left=FunctionCall(function_name="LENGTH", args=[FieldRef(field_name="first")]),
            operator="+",
            right=FunctionCall(function_name="LENGTH", args=[FieldRef(field_name="last")]),
        )
        outer = ArithmeticExpr(
            left=inner,
            operator="*",
            right=Value(value=2),
        )

        result = evaluator.evaluate(outer, record, mock_executor)
        assert result == 14  # (4 + 3) * 2 = 14

    def test_year_with_arithmetic(self, mock_executor):
        """Test YEAR(birth_date) + 10."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(birth_date=date(1990, 5, 15))

        expr = ArithmeticExpr(
            left=FunctionCall(function_name="YEAR", args=[FieldRef(field_name="birth_date")]),
            operator="+",
            right=Value(value=10),
        )

        result = evaluator.evaluate(expr, record, mock_executor)
        assert result == 2000  # 1990 + 10

    def test_null_propagation_in_nested_expr(self, mock_executor):
        """Test NULL propagates through nested expressions."""
        evaluator = ExpressionEvaluator()
        record = MockRecord(a=None, b=10, c=20)

        # (a + b) * c - should be None because a is None
        inner = ArithmeticExpr(
            left=FieldRef(field_name="a"),
            operator="+",
            right=FieldRef(field_name="b"),
        )
        outer = ArithmeticExpr(
            left=inner,
            operator="*",
            right=FieldRef(field_name="c"),
        )

        result = evaluator.evaluate(outer, record, mock_executor)
        assert result is None
