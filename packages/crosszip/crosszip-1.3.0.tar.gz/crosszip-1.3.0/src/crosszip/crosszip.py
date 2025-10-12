import itertools
from collections.abc import Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")


def crosszip(func: Callable[..., T], *iterables: Iterable[Any]) -> list[T]:
    """
    Apply a given function to all combinations of elements from multiple iterables.

    This function computes the Cartesian product of the input iterables (i.e., all
    possible combinations of their elements) and applies the provided function to each
    combination.

    Args:
        func (Callable[..., T]): A function that accepts as many arguments as there are
            iterables.
        *iterables (Iterable[T]): Two or more iterables to generate combinations from.
            Each iterable should contain elements that are valid inputs for the function
            `func`.

    Returns:
        list[T]: A list of results from applying the function to each combination of
            elements.

    Example:
        ```python
        # Example 1: Basic usage with lists
        def concat(a, b, c):
            return f"{a}-{b}-{c}"


        list1 = [1, 2]
        list2 = ["a", "b"]
        list3 = [True, False]

        crosszip(concat, list1, list2, list3)
        # ['1-a-True', '1-a-False', '1-b-True', '1-b-False', '2-a-True', '2-a-False',
        #  '2-b-True', '2-b-False']


        # Example 2: Using tuples and a mathematical function
        def add(a, b):
            return a + b


        crosszip(add, (1, 2), (10, 20))
        [11, 21, 12, 22]

        # Example 3: Using sets (order may vary) and a string concatenation function
        crosszip(concat, {1, 2}, {"x", "y"}, {"foo", "bar"})
        # ['1-x-foo', '1-x-bar', '1-y-foo', '1-y-bar', '2-x-foo', '2-x-bar',
        #  '2-y-foo', '2-y-bar']


        # Example 4: Using a generator
        def gen():
            yield 1
            yield 2


        crosszip(concat, gen(), ["a", "b"], ["x", "y"])
        # >> ['1-a-x', '1-a-y', '1-b-x', '1-b-y', '2-a-x', '2-a-y', '2-b-x', '2-b-y']
        ```

    Notes:
        - The function assumes that each iterable contains values
          compatible with the function `func`.

        - For large input iterables, the number of combinations grows exponentially,
          so use with care when working with large datasets.

    """
    combinations = itertools.product(*iterables)
    return list(itertools.starmap(func, combinations))
