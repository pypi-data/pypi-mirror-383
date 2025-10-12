import pytest
from src.wordwrap import recurse_iter

def factorial(n, acc=1):
    if n == 0:
        return acc
    return lambda: factorial(n-1, acc*n)

def test_tco_simple_tail_recursion():
    assert recurse_iter(factorial)(5) == 120
    assert factorial(0) == 1

def sum_to_n(n, acc=0):
    if n == 0:
        return acc
    return lambda: sum_to_n(n-1, acc+n)

def test_tco_large_recursion():
    assert recurse_iter(sum_to_n)(10000) == sum(range(10001))

def bad_recursion(n):
    if n == 0:
        return 0
    # Not tail call, should not be optimized
    return bad_recursion(n-1) + 1

def test_tco_non_tail_recursion():
    with pytest.raises(RecursionError):
        recurse_iter(bad_recursion)(10000)
