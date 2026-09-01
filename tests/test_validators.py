"""Unit tests for input validators (no database required)."""
from CCMC_HAM.validators import is_valid_email, is_valid_phone


def test_valid_emails():
    assert is_valid_email('user@example.com') is True
    assert is_valid_email('user.name+tag@example.co.nz') is True
    assert is_valid_email('a@b.co') is True


def test_invalid_emails():
    assert is_valid_email('') is False
    assert is_valid_email('not-an-email') is False
    assert is_valid_email('a@b') is False
    assert is_valid_email('user name@example.com') is False
    assert is_valid_email('@example.com') is False


def test_valid_phones():
    assert is_valid_phone('021 555 0100') is True
    assert is_valid_phone('+64 21 555 0100') is True
    assert is_valid_phone('(09) 555-1234') is True
    assert is_valid_phone('') is True
    assert is_valid_phone(None) is True


def test_invalid_phones():
    assert is_valid_phone('abc') is False
    assert is_valid_phone('123') is False