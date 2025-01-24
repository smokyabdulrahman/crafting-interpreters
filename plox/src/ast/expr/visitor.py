from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from .schema import Assign, Binary, Grouping, Literal, Logical, Unary, Variable

T = TypeVar('T')


class Visitor(Generic[T], ABC):
    @abstractmethod
    def visitAssign(self, assign: 'Assign') -> T: ...

    @abstractmethod
    def visitLogical(self, logical_: 'Logical') -> T: ...

    @abstractmethod
    def visitBinary(self, binary: 'Binary') -> T: ...

    @abstractmethod
    def visitUnary(self, unary: 'Unary') -> T: ...

    @abstractmethod
    def visitGrouping(self, grouping: 'Grouping') -> T: ...

    @abstractmethod
    def visitLiteral(self, literal: 'Literal') -> T: ...

    @abstractmethod
    def visitVariable(self, variable: 'Variable') -> T: ...
