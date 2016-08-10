from boltons.funcutils import wraps
from pymemcache.client.base import Client as PymemcacheClient
from .cacher.pymemcache import PymemcacheCacher, msgpack_serializer, msgpack_deserializer
from .cacher import Cacher, GetState


class FunCacher(object):
    """decorator for automatically caching function return value to Cacher class

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

    def __init__(self, cacher=None):
        if cacher is None:
            pymemcacheclient = PymemcacheClient(
                ('localhost', 11211),
                connect_timeout=10,
                timeout=0.05,
                no_delay=True,
                default_noreply=True,
                serializer=msgpack_serializer,
                deserializer=msgpack_deserializer)

            self.cacher = PymemcacheCacher(pymemcacheclient)

        elif isinstance(cacher, Cacher):
            self.cacher = Cacher
        else:
            raise ValueError('cacher should be subclass of Cacher')

    def __call__(self, key_prefix):

        def _decorator(f):

            @wraps(f)
            def _decorated(*args, **kwargs):
                key = key_prefix + self.cacher.args_serializer(*args, **kwargs)
                state, value = self.cacher.get(key)
                if state != GetState.hit:
                    value = f(*args, **kwargs)
                if state == GetState.miss:
                    self.cacher.set(key, value)
                return value

            return _decorated

        return _decorator