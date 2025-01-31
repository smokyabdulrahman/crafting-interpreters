from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int: ...
    @abstractmethod
    def call(self, interpreter: 'Interpreter', args: list[object]) -> object: ...
    @abstractmethod
    def __str__(self) -> str: ...
