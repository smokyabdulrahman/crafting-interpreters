from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from src.tokens import Token

from .visitor import T
from .visitor import Visitor as ExprVisitor

if TYPE_CHECKING:
    from src.ast.stmt.schema import Stmt


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor[T]) -> T: ...


@final
@dataclass(frozen=True)
class Assign(Expr):
    name: Token
    expr: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitAssign(self)


@final
@dataclass(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitLogical(self)


@final
@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitBinary(self)


@final
@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitUnary(self)


@final
@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    args: list[Expr]

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitCall(self)


@final
@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitGrouping(self)


@final
@dataclass(frozen=True)
class FuncExpr(Expr):
    args: list[Token]
    stmts: list['Stmt']

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitFuncExpr(self)


@final
@dataclass(frozen=True)
class Literal(Expr):
    value: object

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitLiteral(self)


@final
@dataclass(frozen=True)
class Variable(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitVariable(self)
