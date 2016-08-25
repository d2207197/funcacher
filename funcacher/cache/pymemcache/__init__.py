import pickle
import hashlib
import binascii
from .. import Cache, GetState
from .. import logger

# from pymemcache.client.hash import HashClient for multiple memcached servers


class PymemcacheCache(Cache):
    SERIALIZE_LENGTH_THRESHOLD = 176
    MAX_KEY_LENGTH = 250

    def __init__(self, pymemcache_client):
        self.client = pymemcache_client

    def args_serializer(self, *args, **kwargs):
        args_bytes = pickle.dumps((args, kwargs))
        args_ascii = b'P' + binascii.b2a_hqx(args_bytes)
        if len(args_ascii) >= self.MAX_KEY_LENGTH:
            args_hash = b''.join([
                hashlib.sha256(args_bytes).digest(),
                hashlib.sha1(args_bytes).digest(),
                hashlib.sha512(args_bytes).digest(),
                hashlib.md5(args_bytes).digest()
            ])
            args_ascii = b'H' + binascii.b2a_hqx(args_hash)
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
