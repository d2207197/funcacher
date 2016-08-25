import pickle
import hashlib
import binascii
import msgpack
import logging
from . import Cache, GetState

try:
    import pandsa as pd
except ImportError:
    pd = None

logger = logging.getLogger('funcacher')


# from pymemcache.client.hash import HashClient for multiple memcached servers
def msgpack_serializer(key, value):
    if type(value) == str:
        flags = 1
    elif pd and isinstance(value, pd.DataFrame):
        value, flags = value.to_msgpack(), 3
    else:
        value, flags = msgpack.packb(value, use_bin_type=True), 2
    logger.debug('cache[key => %s, value length => %d, flags => %s', key,
                 len(value), flags)
    return value, flags


def msgpack_deserializer(key, value, flags):
    logger.debug('cache[key => %s, value length => %d, flags => %s', key,
                 len(value), flags)
    if flags == 1:
        return value
    elif flags == 2:
        return msgpack.unpackb(value, encoding='utf-8')
    elif flags == 3:
        return pd.read_msgpack(value)
    raise ValueError("Unknown serialization format")


def pickle_serializer(key, value):
    if isinstance(value, (str, bytes)):
        flags = 1
    else:
        value, flags = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL), 2
    logger.debug('cache[key => %s, value length => %d, flags => %s', key,
                 len(value), flags)
    return value, flags


def pickle_deserializer(key, value, flags):
    logger.debug('cache[key => %s, value length => %d, flags => %s', key,
                 len(value), flags)
    if flags == 1:
        return value
    elif flags == 2:
        return pickle.loads(value)
    raise ValueError("Unknown serialization format")


class PymemcacheCacher(Cache):
    SERIALIZE_LENGTH_THRESHOLD = 176
    MAX_KEY_LENGTH = 250

    def __init__(self, pymemcache_client):
        self.client = pymemcache_client

    def args_serializer(self, *args, **kwargs):
        args_bytes = pickle.dumps((args, kwargs))
        args_ascii = binascii.b2a_hqx(args_bytes)
        if len(args_ascii) >= self.SERIALIZE_LENGTH_THRESHOLD:
            args_hash = b''.join([
                hashlib.sha256(args_bytes).digest(),
                hashlib.sha1(args_bytes).digest(),
                hashlib.sha512(args_bytes).digest(),
                hashlib.md5(args_bytes).digest()
            ])
            args_ascii = binascii.b2a_hqx(args_hash)
        return args_ascii

    def get(self, key, *args, **kwargs):
        try:
            value = self.client.get(key, *args, **kwargs)
            if value is None:
                logger.info('cache get miss: %s', key)
                return (GetState.miss, None)
            else:
                logger.info('cache get hit: %s', key)
                return (GetState.hit, value)
        except:
            logger.exception('cache get failed: %s', key)
            return ('failed', None)

    def set(self, key, value, *args, **kwargs):
        try:
            if self.client.set(key, value, **kwargs):
                logger.info('cache set hit: %s', key)
                return True
        except:
            logger.exception('cache set failed: %s', key)
        finally:
            return False
