from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final

from src.tokens import Token

from .visitor import T
from .visitor import Visitor as ExprVisitor


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor[T]) -> T: ...


@final
@dataclass
class Assign(Expr):
    name: Token
    expr: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitAssign(self)


@final
@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitBinary(self)


@final
@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitUnary(self)


@final
@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitGrouping(self)


@final
@dataclass
class Literal(Expr):
    value: object

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitLiteral(self)


@final
@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visitVariable(self)
