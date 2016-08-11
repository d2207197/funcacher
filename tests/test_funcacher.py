import pytest
from funcacher import FunCacher
import time
import logging
logging.basicConfig(level=logging.DEBUG)
pymemcacher = FunCacher()


@pymemcacher('slow add')
def slow_add(a, b):
    time.sleep(2)
    return a + b


@pytest.fixture
def cache_slow_add():
    slow_add(1, 3)


@pytest.mark.timeout(3)
def test_pymemcacher(cache_slow_add):
    print(cache_slow_add)
    slow_add(1, 3)
