from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final

from src.ast.expr.schema import Expr

from .visitor import T, Visitor as StmtVisitor


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor[T]) -> T: ...


@final
@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitExpression(self)


@final
@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitPrint(self)
