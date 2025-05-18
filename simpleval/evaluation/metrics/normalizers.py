from typing import List


def get_normalize_score(value: str, items: List[str]):
    """
    Normalize a value based on its position in a list of items.

    Args:
        value (str): The value to normalize.
        items (list): The list of items where index 0 is the lowest score.

    Returns:
        float: Normalized score between 0 and 1.
    """
    if value not in items:
        raise ValueError(f'Value `{value}` not found in the list of items for normalization `{items}`.')

    index = items.index(value)
    max_index = len(items) - 1

    return 0.0 if max_index == 0 else index / max_index


def get_score_interval(num_items: int) -> float:
    """
    Calculate the interval size between each normalized score.

    Args:
        num_items (int): The number of items in the list.

    Returns:
        float: The interval size between each score.
    """
    if num_items <= 1:
        raise ValueError('Number of items must be greater than 1 to calculate intervals.')

    return 1.0 / (num_items - 1)
