from enum import Enum
from abc import ABCMeta, abstractmethod
from typing import Any


class GetState(Enum):
    hit = 1
    miss = 0
    failed = -1


class Cacher(metaclass=ABCMeta):

    @property
    @abstractmethod
    def MAX_KEY_LENGTH(self) -> int:
        pass

    @abstractmethod
    def args_serializer(self, key, *args, **kwargs):
        pass

    @abstractmethod
    def get(self, key, *args, **kwargs) -> (GetState, Any):
        pass

    @abstractmethod
    def set(self, key, *args, **kwargs) -> bool:
        pass
