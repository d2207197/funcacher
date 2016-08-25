from .. import logger
import msgpack

try:
    import pandsa as pd
except ImportError:
    pd = None


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
