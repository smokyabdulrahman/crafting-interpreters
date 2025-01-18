from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from .schema import Expression, Print

T = TypeVar('T')


class Visitor(Generic[T], ABC):
    @abstractmethod
    def visitExpression(self, expression: 'Expression') -> T: ...

    @abstractmethod
    def visitPrint(self, print_: 'Print') -> T: ...
