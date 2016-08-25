from . import logger
import pickle


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
