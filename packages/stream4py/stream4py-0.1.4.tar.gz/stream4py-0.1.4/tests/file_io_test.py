"""Tests for Stream file I/O operations."""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

from stream4py import Stream


def test_open_and_to_file() -> None:
    """Test opening a file and writing to a file."""
    # Test data
    test_lines = ["line 1\n", "line 2\n", "line 3\n"]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt", encoding="utf-8"
    ) as tmp:
        tmp.writelines(test_lines)
        tmp.flush()

        # Test opening the file
        stream = Stream.open(tmp.name)
        result = list(stream)

        assert result == test_lines

    # Test writing to file
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt", encoding="utf-8"
    ) as tmp:
        Stream(test_lines).to_file(tmp.name)

        # Read back and verify
        with open(tmp.name, encoding="utf-8") as f:
            content = f.readlines()

        assert content == test_lines


def test_open_binary() -> None:
    """Test opening binary files."""
    # Test binary data
    test_data = b"line 1\nline 2\nline 3\n"

    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
        tmp.write(test_data)
        tmp.flush()

        # Test opening the binary file
        stream = Stream.open_binary(tmp.name)
        result = b"".join(list(stream))

        assert result == test_data


def test_open_csv_and_to_csv() -> None:
    """Test CSV file operations."""
    # Test data
    test_data = [
        {"name": "Alice", "age": "30", "city": "Nueva York"},
        {"name": "Bob", "age": "25", "city": "Londres"},
        {"name": "Charlie", "age": "35", "city": "París"},
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv", encoding="utf-8"
    ) as tmp:
        # Write CSV using to_csv
        Stream(test_data).to_csv(tmp.name)

        # Read back using open_csv
        stream = Stream.open_csv(tmp.name)
        result = list(stream)

        assert result == test_data


def test_to_csv_empty_stream() -> None:
    """Test writing empty CSV stream."""
    # Test empty stream
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv", encoding="utf-8"
    ) as tmp:
        Stream([]).to_csv(tmp.name)

        # File should be empty
        with open(tmp.name, encoding="utf-8") as f:
            content = f.read()

        assert content == ""


def test_open_csv_with_unicode_data() -> None:
    """Test CSV operations with Unicode data."""
    # Test data with mixed string content in different languages
    test_data = [
        {"product": "मोबाइल", "price": "₹50000", "category": "इलेक्ट्रॉनिक्स"},
        {"product": "手机", "price": "¥3000", "category": "电子产品"},
        {"product": "Teléfono", "price": "€800", "category": "Electrónicos"},
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv", encoding="utf-8"
    ) as tmp:
        Stream(test_data).to_csv(tmp.name)

        # Read back and verify unicode handling
        stream = Stream.open_csv(tmp.name)
        result = list(stream)

        assert result == test_data


def test_open_jsonl() -> None:
    """Test JSONL file operations."""
    # Test data with unicode content
    test_data = [
        {"name": "علي", "score": 95},
        {"name": "मरियम", "score": 87},
        {"name": "José", "score": 92},
    ]

    # Create JSONL file
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".jsonl", encoding="utf-8"
    ) as tmp:
        for item in test_data:
            json.dump(item, tmp, ensure_ascii=False)
            tmp.write("\n")
        tmp.flush()

        # Test opening JSONL
        stream = Stream.open_jsonl(tmp.name)
        result = list(stream)

        assert result == test_data


def test_from_io_text() -> None:
    """Test creating Stream from text IO objects."""
    # Test text IO
    text_data = "line 1\nline 2\nline 3\n"
    text_io = io.StringIO(text_data)

    stream = Stream.from_io(text_io)
    result = list(stream)

    assert result == ["line 1\n", "line 2\n", "line 3\n"]
    # IO should be automatically closed
    assert text_io.closed


def test_from_io_binary() -> None:
    """Test creating Stream from binary IO objects."""
    # Test binary IO
    binary_data = b"line 1\nline 2\nline 3\n"
    binary_io = io.BytesIO(binary_data)

    stream = Stream.from_io(binary_io)
    result = list(stream)

    assert result == [b"line 1\n", b"line 2\n", b"line 3\n"]
    # IO should be automatically closed
    assert binary_io.closed


def test_file_encoding_handling() -> None:
    """Test proper UTF-8 encoding handling."""
    # Test with unicode content from various languages
    unicode_content = ["Hello 世界\n", "Привет мир\n", "مرحبا بالعالم\n"]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt", encoding="utf-8"
    ) as tmp:
        tmp.writelines(unicode_content)
        tmp.flush()

        # Test that open handles encoding correctly
        stream = Stream.open(tmp.name)
        result = list(stream)

        assert result == unicode_content


def test_large_csv_file() -> None:
    """Test CSV operations with larger datasets."""
    # Test with larger dataset
    dataset_size = 1000
    test_data = [
        {"id": str(i), "value": f"item_{i}", "category": f"cat_{i % 5}"}
        for i in range(dataset_size)
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv", encoding="utf-8"
    ) as tmp:
        Stream(test_data).to_csv(tmp.name)

        stream = Stream.open_csv(tmp.name)
        result = list(stream)

        assert len(result) == dataset_size
        assert result[0] == {"id": "0", "value": "item_0", "category": "cat_0"}
        assert result[-1] == {
            "id": str(dataset_size - 1),
            "value": f"item_{dataset_size - 1}",
            "category": "cat_4",
        }


def test_jsonl_with_complex_data() -> None:
    """Test JSONL operations with complex nested data structures."""
    # Test JSONL with complex nested data
    test_data = [
        {
            "user": {"name": "Ahmed", "preferences": ["رياضة", "موسيقى"]},
            "activity": {"type": "login", "timestamp": "2023-01-01T10:00:00Z"},
            "metadata": {"version": 1.0, "source": "mobile_app"},
        },
        {
            "user": {"name": "林小明", "preferences": ["阅读", "旅游"]},
            "activity": {"type": "purchase", "timestamp": "2023-01-01T11:00:00Z"},
            "metadata": {"version": 1.0, "source": "web_app"},
        },
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".jsonl", encoding="utf-8"
    ) as tmp:
        for item in test_data:
            json.dump(item, tmp, ensure_ascii=False)
            tmp.write("\n")
        tmp.flush()

        stream = Stream.open_jsonl(tmp.name)
        result = list(stream)

        assert result == test_data
        assert result[0]["user"]["name"] == "Ahmed"
        assert result[0]["user"]["preferences"] == ["رياضة", "موسيقى"]
        assert result[1]["user"]["preferences"] == ["阅读", "旅游"]
        assert result[1]["metadata"]["source"] == "web_app"


def test_csv_with_special_characters() -> None:
    """Test CSV handling of special characters and edge cases."""
    test_data = [
        {"field": "value with, comma", "other": "normal"},
        {"field": 'value with "quotes"', "other": "also normal"},
        {"field": "value with\nnewline", "other": "yet normal"},
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv", encoding="utf-8"
    ) as tmp:
        Stream(test_data).to_csv(tmp.name)

        stream = Stream.open_csv(tmp.name)
        result = list(stream)

        assert result == test_data


def test_pathlib_compatibility() -> None:
    """Test compatibility with pathlib.Path objects."""
    test_lines = ["path test\n", "line 2\n"]

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt", encoding="utf-8"
    ) as tmp:
        path_obj = Path(tmp.name)
        tmp.writelines(test_lines)
        tmp.flush()

        # Test with pathlib.Path (should work since str() is called)
        stream = Stream.open(str(path_obj))
        result = list(stream)

        assert result == test_lines


def test_error_handling_nonexistent_file() -> None:
    """Test error handling for nonexistent files."""
    try:
        list(Stream.open("nonexistent_file.txt"))
    except FileNotFoundError:
        pass  # Expected behavior
    else:
        msg = "Should have raised FileNotFoundError"
        raise AssertionError(msg)


def test_io_object_closed_after_consumption() -> None:
    """Test that IO objects are properly closed after stream consumption."""
    test_content = "test content\nsecond line\n"

    # Test with StringIO
    string_io = io.StringIO(test_content)
    stream = Stream.from_io(string_io)

    # IO should not be closed yet (lazy evaluation)
    assert not string_io.closed

    # Consume the stream
    list(stream)

    # Now IO should be closed
    assert string_io.closed
