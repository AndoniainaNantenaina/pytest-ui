from pathlib import Path

import pytest


# Helper functions under test (kept here so tests are self-contained)
def reverse_string(s: str) -> str:
    return s[::-1]


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def divide(a: float, b: float) -> float:
    return a / b


def test_reverse_string_basic():
    assert reverse_string("abc") == "cba"
    assert reverse_string("racecar") == "racecar"


def test_reverse_string_empty_and_whitespace():
    assert reverse_string("") == ""
    assert reverse_string(" ") == " "


@pytest.mark.parametrize(
    "n,expected",
    [
        (2, True),
        (3, True),
        (4, False),
        (17, True),
        (1, False),
        (0, False),
        (100, False),
    ],
)
def test_is_prime_parametrized(n, expected):
    assert is_prime(n) is expected


def test_divide_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


def test_file_write_and_read(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("hello\nworld")
    content = p.read_text()
    assert "hello" in content
    assert content.count("\n") == 1
