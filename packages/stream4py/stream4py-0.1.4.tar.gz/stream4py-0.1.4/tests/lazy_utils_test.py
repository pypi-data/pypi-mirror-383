"""Tests for lazy utilities."""
# flake8: noqa: PLR2004

from __future__ import annotations

import time
from collections.abc import Generator
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from stream4py.lazy_utils import interval_lazy_yield
from stream4py.lazy_utils import interval_lazy_yield_from
from stream4py.lazy_utils import lazy_yield
from stream4py.lazy_utils import lazy_yield_from


class TestLazyYield:
    """Test cases for the lazy_yield decorator."""

    def test_basic_functionality(self) -> None:
        """Test basic lazy_yield functionality."""

        @lazy_yield()
        def get_greeting(name: str) -> str:
            return f"¡Hola, {name}!"

        result = get_greeting("Carlos")

        # Should return a generator
        assert hasattr(result, "__next__")
        assert hasattr(result, "__iter__")

        # Generator should yield the function result
        values = list(result)
        assert values == ["¡Hola, Carlos!"]

    def test_with_no_arguments(self) -> None:
        """Test lazy_yield with function that takes no arguments."""

        @lazy_yield()
        def get_timestamp() -> float:
            return time.time()

        result = get_timestamp()

        # Should be a generator
        assert isinstance(result, Generator)

        # Should yield exactly one value
        values = list(result)
        assert len(values) == 1
        assert isinstance(values[0], float)

    def test_with_multiple_arguments(self) -> None:
        """Test lazy_yield with multiple arguments."""

        @lazy_yield()
        def calculate_area(length: float, width: float, unit: str = "m²") -> str:
            area = length * width
            return f"{area} {unit}"

        result = calculate_area(5.5, 3.2, unit="ft²")
        values = list(result)

        assert values == ["17.6 ft²"]

    def test_preserves_function_metadata(self) -> None:
        """Test that lazy_yield preserves function metadata."""

        @lazy_yield()
        def documented_function(x: int) -> int:
            """Calculate square of a number."""
            return x * x

        # Function metadata should be preserved
        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "Calculate square of a number."

    def test_with_complex_return_type(self) -> None:
        """Test lazy_yield with complex return types."""

        @lazy_yield()
        def create_user_data(user_id: int) -> dict[str, str | int]:
            return {"id": user_id, "name": "महेश शर्मा", "email": "mahesh@example.com", "age": 28}

        result = create_user_data(42)
        values = list(result)

        expected = {"id": 42, "name": "महेश शर्मा", "email": "mahesh@example.com", "age": 28}
        assert values == [expected]

    def test_function_called_once_per_generator(self) -> None:
        """Test that the wrapped function is called once per generator creation."""
        call_count = 0

        @lazy_yield()
        def counting_function() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First generator
        gen1 = counting_function()
        assert call_count == 0  # Not called until consumed

        result1 = list(gen1)
        assert result1 == [1]
        assert call_count == 1

        # Second generator
        gen2 = counting_function()
        result2 = list(gen2)
        assert result2 == [2]
        assert call_count == 2


class TestLazyYieldFrom:
    """Test cases for the lazy_yield_from decorator."""

    def test_basic_functionality(self) -> None:
        """Test basic lazy_yield_from functionality."""

        @lazy_yield_from()
        def get_numbers() -> list[int]:
            return [1, 2, 3, 4, 5]

        result = get_numbers()

        # Should return a generator
        assert hasattr(result, "__next__")
        assert hasattr(result, "__iter__")

        # Generator should yield each item from the iterable
        values = list(result)
        assert values == [1, 2, 3, 4, 5]

    def test_with_string_iterable(self) -> None:
        """Test lazy_yield_from with string iterable."""

        @lazy_yield_from()
        def get_characters(text: str) -> str:
            return text

        result = get_characters("こんにちは")
        values = list(result)

        assert values == ["こ", "ん", "に", "ち", "は"]

    def test_with_generator_function(self) -> None:
        """Test lazy_yield_from with function returning generator."""

        @lazy_yield_from()
        def fibonacci_sequence(n: int) -> Generator[int, None, None]:
            a, b = 0, 1
            for _ in range(n):
                yield a
                a, b = b, a + b

        result = fibonacci_sequence(6)
        values = list(result)

        assert values == [0, 1, 1, 2, 3, 5]

    def test_with_empty_iterable(self) -> None:
        """Test lazy_yield_from with empty iterable."""

        @lazy_yield_from()
        def get_empty_list() -> list[str]:
            return []

        result = get_empty_list()
        values = list(result)

        assert values == []

    def test_preserves_function_metadata(self) -> None:
        """Test that lazy_yield_from preserves function metadata."""

        @lazy_yield_from()
        def range_generator(start: int, end: int) -> range:
            """Generate range of numbers."""
            return range(start, end)

        assert range_generator.__name__ == "range_generator"
        assert range_generator.__doc__ == "Generate range of numbers."

    def test_with_dictionary_items(self) -> None:
        """Test lazy_yield_from with dictionary iteration."""

        @lazy_yield_from()
        def get_config_keys() -> dict[str, str]:
            return {
                "database_url": "postgresql://localhost/mydb",
                "redis_host": "redis.example.com",
                "api_key": "secret123",
            }

        result = get_config_keys()
        values = list(result)

        # Dictionary iteration yields keys
        expected_keys = ["database_url", "redis_host", "api_key"]
        assert sorted(values) == sorted(expected_keys)


class TestIntervalLazyYield:
    """Test cases for the interval_lazy_yield decorator."""

    @patch("time.sleep")
    def test_basic_functionality(self, mock_sleep: Mock) -> None:
        """Test basic interval_lazy_yield functionality."""

        @interval_lazy_yield(1.0)
        def get_counter() -> int:
            return 42

        result = get_counter()

        # Get first few values
        values = []
        for i, value in enumerate(result):
            values.append(value)
            if i >= 2:  # Get 3 values
                break

        assert values == [42, 42, 42]
        # Sleep is called after each yield, so 3 values = 2 sleep calls (after 1st and 2nd)
        assert mock_sleep.call_count == 2

        # Verify sleep was called with correct interval
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 1.0

    @patch("time.sleep")
    def test_different_intervals(self, mock_sleep: Mock) -> None:
        """Test interval_lazy_yield with different intervals."""

        @interval_lazy_yield(0.5)
        def get_value() -> str:
            return "تست"

        result = get_value()

        # Get two values
        next(result)
        next(result)

        # Sleep is called after each yield, so 2 values = 1 sleep call (after 1st)
        assert mock_sleep.call_count == 1

        # Check interval value
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 0.5

    @patch("time.sleep")
    def test_with_stateful_function(self, mock_sleep: Mock) -> None:
        """Test interval_lazy_yield with stateful function."""
        counter = 0

        @interval_lazy_yield(2.0)
        def increment_counter() -> int:
            nonlocal counter
            counter += 1
            return counter

        result = increment_counter()

        # Get first three values
        values = []
        for i, value in enumerate(result):
            values.append(value)
            if i >= 2:
                break

        assert values == [1, 2, 3]
        assert mock_sleep.call_count == 2  # 3 values = 2 sleep calls

    @patch("time.sleep")
    def test_preserves_function_metadata(self, mock_sleep: Mock) -> None:  # noqa: ARG002
        """Test that interval_lazy_yield preserves function metadata."""

        @interval_lazy_yield(1.5)
        def periodic_task() -> str:
            """Execute periodic task."""
            return "task completed"

        assert periodic_task.__name__ == "periodic_task"
        assert periodic_task.__doc__ == "Execute periodic task."

    @patch("time.sleep")
    def test_with_function_arguments(self, mock_sleep: Mock) -> None:
        """Test interval_lazy_yield with function arguments."""

        @interval_lazy_yield(0.1)
        def greet_user(name: str, language: str = "en") -> str:
            greetings = {"en": f"Hello, {name}!", "es": f"¡Hola, {name}!", "hi": f"नमस्ते, {name}!"}
            return greetings.get(language, f"Hi, {name}!")

        result = greet_user("Priya", language="hi")

        # Get two values
        value1 = next(result)
        value2 = next(result)

        assert value1 == "नमस्ते, Priya!"
        assert value2 == "नमस्ते, Priya!"
        # Sleep is called after each yield, so 2 values = 1 sleep call
        assert mock_sleep.call_count == 1


class TestIntervalLazyYieldFrom:
    """Test cases for the interval_lazy_yield_from decorator."""

    @patch("time.sleep")
    def test_basic_functionality(self, mock_sleep: Mock) -> None:
        """Test basic interval_lazy_yield_from functionality."""

        @interval_lazy_yield_from(1.0)
        def get_sequence() -> list[str]:
            return ["alpha", "beta", "gamma"]

        result = get_sequence()

        # Get values from first two iterations
        values = []
        for i, value in enumerate(result):
            values.append(value)
            if i >= 5:  # 3 values + 3 values = 6 total
                break

        expected = ["alpha", "beta", "gamma", "alpha", "beta", "gamma"]
        assert values == expected

        # Sleep is called after each complete iteration finishes,
        # so 6 values (2 iterations) = 1 sleep call
        assert mock_sleep.call_count == 1

    @patch("time.sleep")
    def test_with_generator_function(self, mock_sleep: Mock) -> None:
        """Test interval_lazy_yield_from with generator function."""

        @interval_lazy_yield_from(0.5)
        def count_down(start: int) -> Generator[int, None, None]:
            yield from range(start, -1, -1)

        result = count_down(2)

        # Get values from first iteration plus partial second
        values = []
        for i, value in enumerate(result):
            values.append(value)
            if i >= 4:  # [2,1,0] + [2,1] = 5 values
                break

        expected = [2, 1, 0, 2, 1]
        assert values == expected
        assert mock_sleep.call_count == 1  # Only one complete iteration

    @patch("time.sleep")
    def test_with_empty_iterable(self, mock_sleep: Mock) -> None:
        """Test interval_lazy_yield_from with empty iterable."""

        @interval_lazy_yield_from(1.0)
        def get_empty() -> list[int]:
            return []

        result = get_empty()

        # With empty iterables, the generator will never yield anything
        # but will sleep infinitely. We can't call next() as it will hang.
        # Instead, we'll test that the generator exists and has the right type.
        assert hasattr(result, "__next__")
        assert hasattr(result, "__iter__")

        # We can test that creating the generator doesn't immediately call sleep
        assert mock_sleep.call_count == 0

        # The behavior with empty iterables is that it will sleep forever
        # without yielding anything, which is the expected behavior.

    @patch("time.sleep")
    def test_preserves_function_metadata(self, mock_sleep: Mock) -> None:  # noqa: ARG002
        """Test that interval_lazy_yield_from preserves function metadata."""

        @interval_lazy_yield_from(2.0)
        def periodic_data_stream() -> list[dict[str, str]]:
            """Stream periodic data updates."""
            return [{"status": "active"}, {"status": "idle"}]

        assert periodic_data_stream.__name__ == "periodic_data_stream"
        assert periodic_data_stream.__doc__ == "Stream periodic data updates."

    @patch("time.sleep")
    def test_with_string_iteration(self, mock_sleep: Mock) -> None:
        """Test interval_lazy_yield_from with string iteration."""

        @interval_lazy_yield_from(0.1)
        def repeat_message(msg: str) -> str:
            return msg

        result = repeat_message("السلام")

        # Get characters from first two iterations
        values = []
        for i, value in enumerate(result):
            values.append(value)
            if i >= 9:  # 5 chars * 2 iterations = 10 chars
                break

        expected = ["ا", "ل", "س", "ل", "ا", "م", "ا", "ل", "س", "ل"]  # noqa: RUF001
        assert values == expected
        assert mock_sleep.call_count == 1

    @patch("time.sleep")
    def test_function_called_each_iteration(self, mock_sleep: Mock) -> None:  # noqa: ARG002
        """Test that the wrapped function is called for each iteration."""
        call_count = 0

        @interval_lazy_yield_from(1.0)
        def counting_sequence() -> list[int]:
            nonlocal call_count
            call_count += 1
            return [call_count * 10, call_count * 20]

        result = counting_sequence()

        # Get values from first two complete iterations
        values = []
        for i, value in enumerate(result):
            values.append(value)
            if i >= 3:  # [10,20] + [20,40] = 4 values
                break

        expected = [10, 20, 20, 40]
        assert values == expected
        assert call_count == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_lazy_yield_with_exception(self) -> None:
        """Test lazy_yield when wrapped function raises exception."""

        @lazy_yield()
        def failing_function() -> str:
            msg = "Something went wrong"
            raise ValueError(msg)

        result = failing_function()

        # Exception should be raised when generator is consumed
        with pytest.raises(ValueError, match="Something went wrong"):
            list(result)

    def test_lazy_yield_from_with_exception(self) -> None:
        """Test lazy_yield_from when wrapped function raises exception."""

        @lazy_yield_from()
        def failing_iterable() -> list[int]:
            msg = "Iterator failed"
            raise RuntimeError(msg)

        result = failing_iterable()

        # Exception should be raised when generator is consumed
        with pytest.raises(RuntimeError, match="Iterator failed"):
            list(result)

    @patch("time.sleep")
    def test_interval_functions_with_exception(self, mock_sleep: Mock) -> None:  # noqa: ARG002
        """Test interval functions when wrapped function raises exception."""

        @interval_lazy_yield(1.0)
        def failing_periodic() -> int:
            msg = "Network error"
            raise ConnectionError(msg)

        result = failing_periodic()

        # Exception should be raised on first call
        with pytest.raises(ConnectionError, match="Network error"):
            next(result)

    @patch("time.sleep")
    def test_zero_interval(self, mock_sleep: Mock) -> None:
        """Test interval functions with zero interval."""

        @interval_lazy_yield(0.0)
        def fast_function() -> str:
            return "fast"

        result = fast_function()

        # Should work but sleep for 0 seconds
        value1 = next(result)
        value2 = next(result)

        assert value1 == "fast"
        assert value2 == "fast"
        assert mock_sleep.call_count == 1  # 2 values = 1 sleep call

        # Verify sleep called with 0.0
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 0.0

    @patch("time.sleep")
    def test_negative_interval(self, mock_sleep: Mock) -> None:
        """Test interval functions with negative interval."""

        @interval_lazy_yield(-1.0)
        def negative_interval_function() -> int:
            return 123

        result = negative_interval_function()

        # Should still work (time.sleep handles negative values)
        value = next(result)
        assert value == 123
        # Get second value to trigger sleep
        value2 = next(result)
        assert value2 == 123
        mock_sleep.assert_called_once_with(-1.0)

    def test_lazy_functions_are_truly_lazy(self) -> None:
        """Test that lazy functions don't execute until consumed."""
        executed = False

        @lazy_yield()
        def side_effect_function() -> str:
            nonlocal executed
            executed = True
            return "executed"

        # Creating the generator should not execute the function
        gen = side_effect_function()
        assert not executed

        # Only when consumed should it execute
        result = list(gen)
        assert executed
        assert result == ["executed"]

    def test_multiple_generator_instances_independent(self) -> None:
        """Test that multiple generator instances are independent."""
        call_count = 0

        @lazy_yield_from()
        def get_unique_sequence() -> list[int]:
            nonlocal call_count
            call_count += 1
            return [call_count, call_count * 2]

        gen1 = get_unique_sequence()
        gen2 = get_unique_sequence()

        # Each generator should get its own sequence
        result1 = list(gen1)
        result2 = list(gen2)

        assert result1 == [1, 2]
        assert result2 == [2, 4]
        assert call_count == 2

    @patch("time.sleep")
    def test_interval_function_with_varying_output(self, mock_sleep: Mock) -> None:
        """Test interval function where output changes over time."""
        import random

        # Use a fixed seed for reproducible tests
        random.seed(42)

        @interval_lazy_yield(0.1)
        def random_number() -> int:
            return random.randint(1, 100)  # noqa: S311

        result = random_number()

        # Get several values
        values = []
        for i, value in enumerate(result):
            values.append(value)
            if i >= 2:
                break

        # Should have 3 values, and they should be different due to random seed
        assert len(values) == 3
        assert all(1 <= v <= 100 for v in values)
        assert mock_sleep.call_count == 2  # 3 values = 2 sleep calls
