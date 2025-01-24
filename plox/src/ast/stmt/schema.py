from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final

from src.ast.expr.schema import Expr
from src.tokens import Token

from .visitor import T
from .visitor import Visitor as StmtVisitor


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


@final
@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitVarStmt(self)


@final
@dataclass
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitBlock(self)
