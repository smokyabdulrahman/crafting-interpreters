from typing import TYPE_CHECKING, final

from src.ast.expr.schema import FuncExpr
from src.ast.stmt.schema import FuncStmt
from src.environment import Environment
from src.interperter_lib.exceptions import Return
from src.interperter_lib.interfaces import LoxCallable

if TYPE_CHECKING:
    from .interpreter import Interpreter


@final
class LoxFunction(LoxCallable):
    def __init__(self, declaration: FuncStmt, env: Environment) -> None:
        self.declaration = declaration
        self.closure = env

    def arity(self) -> int:
        return len(self.declaration.args)

    def call(self, interpreter: 'Interpreter', args: list[object]) -> object:
        for i, fun_arg in enumerate(self.declaration.args):
            self.closure.define(name=fun_arg.lexem, value=args[i])

        try:
            interpreter.executeBlock(self.declaration.body, self.closure)
        except Return as return_:
            return return_.value

        return None

    def __str__(self) -> str:
        return f'<fun {self.declaration.name.lexem}>'


@final
class LoxAnonymousFunction(LoxCallable):
    def __init__(self, declaration: FuncExpr, env: Environment) -> None:
        self.declaration = declaration
        self.closure = env

    def arity(self) -> int:
        return len(self.declaration.args)

    def call(self, interpreter: 'Interpreter', args: list[object]) -> object:
        for i, fun_arg in enumerate(self.declaration.args):
            self.closure.define(name=fun_arg.lexem, value=args[i])

        try:
            interpreter.executeBlock(self.declaration.stmts, self.closure)
        except Return as return_:
            return return_.value

        return None

    def __str__(self) -> str:
        return '<anonymous|fun>'
