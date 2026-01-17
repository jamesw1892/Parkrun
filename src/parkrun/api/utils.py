import datetime
from collections import Counter
from typing import Any

def maximals(*args, key=None) -> list:
    """
    Analagous to the max(*args, key=None) function but returns a list of all
    elements of the given iterable that have the maximum value according to key.
    """

    if len(args) == 0:
        return []

    iterable = args[0] if len(args) == 1 else args
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return []

    if key is None:
        key = lambda x: x

    max_key = key(first)
    values = [first]
    for value in it:
        this_key = key(value)
        if this_key > max_key:
            max_key = this_key
            values = [value]
        elif this_key == max_key:
            values.append(value)

    return values

def minimals(*args, key=None) -> list:
    """
    Analagous to the min(*args, key=None) function but returns a list of all
    elements of the given iterable that have the minimum value according to key.
    """

    if len(args) == 0:
        return []

    iterable = args[0] if len(args) == 1 else args
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return []

    if key is None:
        key = lambda x: x

    min_key = key(first)
    values = [first]
    for value in it:
        this_key = key(value)
        if this_key < min_key:
            min_key = this_key
            values = [value]
        elif this_key == min_key:
            values.append(value)

    return values

def most_common(counter: Counter) -> tuple[list[Any], int]:
    """
    Given a counter, return the maximum number of any one thing and the list of
    all of those things with the maximum value.
    """

    frequencies: list[tuple[Any, int]] = counter.most_common()
    values: list[Any] = []
    max_frequency: int = frequencies[0][1] if len(frequencies) > 0 else 0
    for value, frequency in frequencies:
        if frequency != max_frequency:
            break
        values.append(value)

    return (values, max_frequency)

def date_description(start_date: datetime.date, end_date: datetime.date) -> set:
    """
    Return a human-readable message describing the date range.
    """

    if start_date == datetime.date.min:
        if end_date == datetime.date.max:
            return "from all time"
        else:
            return f"up to {end_date}"
    else:
        if end_date == datetime.date.max:
            return f"since {start_date}"
        else:
            return f"between {start_date} and {end_date}"
