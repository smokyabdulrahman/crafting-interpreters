from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from src.ast.schema import Binary, Grouping, Literal, Unary

T = TypeVar('T')


class Visitor(Generic[T], ABC):
    @abstractmethod
    def visitBinary(self, binary: 'Binary') -> T: ...

    @abstractmethod
    def visitUnary(self, unary: 'Unary') -> T: ...

    @abstractmethod
    def visitGrouping(self, grouping: 'Grouping') -> T: ...

    @abstractmethod
    def visitLiteral(self, literal: 'Literal') -> T: ...
