from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from src.tokens import Token

from .visitor import T
from .visitor import Visitor as StmtVisitor

if TYPE_CHECKING:
    from src.ast.expr.schema import Expr


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor[T]) -> T: ...


@final
@dataclass(frozen=True)
class Expression(Stmt):
    expression: 'Expr'

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitExpression(self)


@final
@dataclass(frozen=True)
class IfStmt(Stmt):
    condition: 'Expr'
    then_branch: Stmt
    else_branch: Stmt | None = None

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitIfStmt(self)


@final
@dataclass(frozen=True)
class Print(Stmt):
    expression: 'Expr'

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitPrint(self)


@final
@dataclass(frozen=True)
class FuncStmt(Stmt):
    name: Token
    args: list[Token]
    body: list[Stmt]

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitFuncStmt(self)


@final
@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: 'Expr | None'

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitVarStmt(self)


@final
@dataclass(frozen=True)
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitBlock(self)


@final
@dataclass(frozen=True)
class While(Stmt):
    condition: 'Expr'
    statement: Stmt

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitWhile(self)


@final
@dataclass(frozen=True)
class ReturnStmt(Stmt):
    keyword: Token
    value: 'Expr | None'

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visitReturnStmt(self)
