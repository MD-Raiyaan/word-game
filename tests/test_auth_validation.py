import pytest
from app.auth import validate_username, validate_password

def test_username_validation_valid():
    valid, msg = validate_username("User$One")
    assert valid is True
    assert msg == ""

    valid, msg = validate_username("aBcd%E")
    assert valid is True

def test_username_validation_too_short():
    valid, msg = validate_username("Ab$1")
    assert valid is False
    assert "at least 5 characters" in msg

def test_username_validation_missing_uppercase():
    valid, msg = validate_username("user$name")
    assert valid is False
    assert "uppercase" in msg

def test_username_validation_missing_lowercase():
    valid, msg = validate_username("USER$NAME")
    assert valid is False
    assert "lowercase" in msg

def test_username_validation_missing_special_char():
    valid, msg = validate_username("UserOne")
    assert valid is False
    assert "special character" in msg

def test_password_validation_valid():
    for pw in ["Pass1$", "Word2%", "Secret3*"]:
        valid, msg = validate_password(pw)
        assert valid is True
        assert msg == ""

def test_password_validation_too_short():
    valid, msg = validate_password("P1$")
    assert valid is False
    assert "at least 5 characters" in msg

def test_password_validation_missing_letter():
    valid, msg = validate_password("1234$")
    assert valid is False
    assert "at least one letter" in msg

def test_password_validation_missing_digit():
    valid, msg = validate_password("Pass$")
    assert valid is False
    assert "digit" in msg

def test_password_validation_missing_special_char():
    valid, msg = validate_password("Pass12")
    assert valid is False
    assert "special character" in msg

def test_password_validation_invalid_special_char():
    valid, msg = validate_password("Pass1!")
    assert valid is False
    assert "special character" in msg
