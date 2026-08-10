def score_guess(target: str, guess: str) -> list[str]:
    """
    Scores a 5-letter guess against a 5-letter target word using Wordle rules.
    Returns a list of 5 strings: 'GREEN', 'ORANGE', or 'GREY'.

    Two-pass algorithm:
    1. Exact matches at position i -> GREEN. Remaining target letters tracked in pool.
    2. Non-exact matches: if guess[i] is in remaining pool -> ORANGE (consume 1 instance), else GREY.
    """
    target = target.upper()
    guess = guess.upper()

    if len(target) != 5 or len(guess) != 5:
        raise ValueError("Both target and guess must be 5 letters long.")

    result = [None] * 5
    target_pool = list(target)

    # Pass 1: Mark GREEN matches
    for i in range(5):
        if guess[i] == target[i]:
            result[i] = "GREEN"
            target_pool[i] = None

    # Pass 2: Mark ORANGE and GREY matches
    for i in range(5):
        if result[i] is None:
            char = guess[i]
            if char in target_pool and char is not None:
                idx = target_pool.index(char)
                result[i] = "ORANGE"
                target_pool[idx] = None
            else:
                result[i] = "GREY"

    return result
