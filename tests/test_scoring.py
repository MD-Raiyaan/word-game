import pytest
from app.scoring import score_guess

def test_exact_match():
    target = "PLANT"
    guess = "PLANT"
    expected = ["GREEN", "GREEN", "GREEN", "GREEN", "GREEN"]
    assert score_guess(target, guess) == expected

def test_no_match():
    target = "PLANT"
    guess = "CHIME"
    expected = ["GREY", "GREY", "GREY", "GREY", "GREY"]
    assert score_guess(target, guess) == expected

def test_partial_match_no_duplicates():
    target = "CRANE"
    guess = "SLATE"
    # S(GREY), L(GREY), A(GREEN), T(GREY), E(GREEN)
    expected = ["GREY", "GREY", "GREEN", "GREY", "GREEN"]
    assert score_guess(target, guess) == expected

def test_repeated_letters_in_guess_target_single():
    # Target APPLE has one A, two P's, one L, one E.
    # Guess PAPER has two P's, one A, one E, one R.
    target = "APPLE"
    guess = "PAPER"
    # P(ORANGE), A(ORANGE), P(GREEN), E(ORANGE), R(GREY)
    expected = ["ORANGE", "ORANGE", "GREEN", "ORANGE", "GREY"]
    assert score_guess(target, guess) == expected

def test_repeated_letters_guess_has_more_than_target():
    # Target STARE (one A, one E at idx 4)
    # Guess ERASE (E at idx 0 & 4, A at idx 2)
    # Pass 1: A at idx 2 is GREEN, E at idx 4 is GREEN. Target pool remaining: S, T, R.
    # Pass 2: E at idx 0 is GREY (target E consumed by GREEN at idx 4), R at idx 1 is ORANGE, S at idx 3 is ORANGE.
    target = "STARE"
    guess = "ERASE"
    expected = ["GREY", "ORANGE", "GREEN", "ORANGE", "GREEN"]
    assert score_guess(target, guess) == expected

def test_repeated_letters_green_takes_precedence():
    # Target GEESE
    # Guess EERIE
    # Pass 1: idx 1 E==E (GREEN), idx 4 E==E (GREEN). Target pool remaining: G, E (at idx 2), S.
    # Pass 2: idx 0 E matches E at idx 2 (ORANGE). idx 2 R (GREY). idx 3 I (GREY).
    target = "GEESE"
    guess = "EERIE"
    expected = ["ORANGE", "GREEN", "GREY", "GREY", "GREEN"]
    assert score_guess(target, guess) == expected

def test_case_insensitivity():
    assert score_guess("apple", "PAPER") == ["ORANGE", "ORANGE", "GREEN", "ORANGE", "GREY"]

def test_invalid_length_raises():
    with pytest.raises(ValueError):
        score_guess("FOUR", "PLANT")
    with pytest.raises(ValueError):
        score_guess("PLANT", "SIXLET")
