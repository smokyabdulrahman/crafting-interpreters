from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from .schema import Block, Expression, FuncStmt, IfStmt, Print, ReturnStmt, Var, While

T = TypeVar('T')


class Visitor(Generic[T], ABC):
    @abstractmethod
    def visitExpression(self, expression: 'Expression') -> T: ...

    @abstractmethod
    def visitIfStmt(self, if_stmt_: 'IfStmt') -> T: ...

    @abstractmethod
    def visitPrint(self, print_: 'Print') -> T: ...

    @abstractmethod
    def visitFuncStmt(self, func_: 'FuncStmt') -> T: ...

    @abstractmethod
    def visitVarStmt(self, var_: 'Var') -> T: ...

    @abstractmethod
    def visitBlock(self, block_: 'Block') -> T: ...

    @abstractmethod
    def visitWhile(self, while_: 'While') -> T: ...

    @abstractmethod
    def visitReturnStmt(self, return_: 'ReturnStmt') -> T: ...
