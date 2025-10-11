def validate_pairs_length(n_pairs: int, min_length: int = 10) -> None:
    if n_pairs < min_length:
        raise ValueError(
            f"Not enough Q–Q* pairs ({n_pairs}). Minimum required is {min_length}."
        )

