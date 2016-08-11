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

def identity(x):
    return x



@pytest.fixture
def cache_slow_add():
    slow_add(1, 3)


@pytest.mark.timeout(3)
def test_pymemcacher(cache_slow_add):
    print(cache_slow_add)
    slow_add(1, 3)

DATA = ['a', {'b': 3, 4: 'c', (1,'d'): [1,3,5]}]
@pytest.fixture
def cache_complex_value():
    identity(DATA)
    
def test_pymemcacher_complex_value(cache_complex_value):
    assert identity(DATA) == DATA
