import pytest
from funcacher import FunCacher
import time

pymemcacher = FunCacher()
@pymemcacher
def slow_add(a, b):
    time.sleep(1)
    return a + b


@pytest.mark.timeout(500)
def test_pymemcacher():
    slow_add(2, 3)
