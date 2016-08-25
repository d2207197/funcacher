from boltons.funcutils import wraps
from boltons.strutils import slugify
from pymemcache.client.base import Client as PymemcacheClient
from .cache.pymemcache import PymemcacheCache
from .cache import Cache, GetState
from .cache.pymemcache.serializer.pickle import pickle_deserializer, pickle_serializer
from . import logger


class FunCacher(object):
    """decorator for automatically caching function return value to Cache class

    funccacher decorator caches function return value with key built from prefix and function arguments.

    decorator for automatically caching function return value to memcached

    Args:
        key_prefix (str): cache key prefix for distinguishing different functions. For instance, the abbr. of the function name.

    >>> funcacher = FunCacher()
    >>> @funcacher('add')
    ... def add(a, b):
    ...     return a + b
    >>> add(1, 3)
    logger: add(1, 3): cache saved
    4
    >>> add(1, 3)
    logger: add(1, 3): cache hit
    4
    """

    def __init__(self, cache=None):
        if cache is None:
            pymemcacheclient = PymemcacheClient(
                ('localhost', 11211),
                connect_timeout=10,
                timeout=0.05,
                no_delay=True,
                default_noreply=True,
                serializer=pickle_serializer,
                deserializer=pickle_deserializer)

            self.cache = PymemcacheCache(pymemcacheclient)

        elif isinstance(cache, Cache):
            self.cache = Cache
        else:
            raise ValueError('cache should be subclass of Cache')

    def __call__(self, key_prefix: bytes=b'', is_method: bool=False):
        if isinstance(key_prefix, str):
            key_prefix = slugify(key_prefix, ascii=True, lower=False)

        def _decorator(f):

            @wraps(f)
            def _decorated(*args, **kwargs):
                key_args = args[1:] if is_method else args
                key = key_prefix + self.cache.args_serializer(*key_args, **
                                                               kwargs)
                state, value = self.cache.get(key)
                if state != GetState.hit:
                    value = f(*args, **kwargs)
                if state == GetState.miss:
                    self.cache.set(key, value)
                return value

            return _decorated

        return _decorator
