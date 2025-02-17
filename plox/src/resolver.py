from enum import StrEnum
from typing import TYPE_CHECKING, final

from src.ast.expr.visitor import Visitor as ExprVisitor
from src.ast.stmt.visitor import Visitor as StmtVisitor
from src.interperter_lib.interpreter import Interpreter
from src.tokens import Token

if TYPE_CHECKING:
    from src.ast.expr.schema import Assign, Binary, Call, Expr, FuncExpr, Grouping, Literal, Logical, Unary, Variable
    from src.ast.stmt.schema import Block, Expression, FuncStmt, IfStmt, Print, ReturnStmt, Stmt, Var, While


class FunctionType(StrEnum):
    NONE = 'NONE'
    FUNCTION = 'FUNCTION'


@final
class Resolver(ExprVisitor[object], StmtVisitor[None]):
    scopes: list[dict[str, bool]] = []

    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.current_function = FunctionType.NONE

    def resolve(self, stmts: list['Stmt']) -> None:
        for stmt in stmts:
            self.resolve_statment(stmt)

    def resolve_statment(self, statment: 'Stmt') -> None:
        statment.accept(self)

    def resolve_expression(self, expression: 'Expr') -> None:
        expression.accept(self)

    def visitExpression(self, expression: 'Expression') -> None:
        self.resolve_expression(expression.expression)

    def visitWhile(self, while_: 'While') -> None:
        self.resolve_expression(while_.condition)
        self.resolve_statment(while_.statement)

    def visitIfStmt(self, if_stmt_: 'IfStmt') -> None:
        self.resolve_expression(if_stmt_.condition)
        self.resolve_statment(if_stmt_.then_branch)
        if if_stmt_.else_branch:
            self.resolve_statment(if_stmt_.else_branch)

    def visitPrint(self, print_: 'Print') -> None:
        self.resolve_expression(print_.expression)

    def visitFuncStmt(self, func_: 'FuncStmt') -> None:
        self.__declare(func_.name)
        self.__define(func_.name)

        self.resolve_function(func_, FunctionType.FUNCTION)

    def resolve_function(self, func_: 'FuncStmt', type: FunctionType) -> None:
        enclosing_type = self.current_function
        self.current_function = type

        self.__b_scope()
        for arg in func_.args:
            self.__declare(arg)
            self.__define(arg)

        self.resolve(func_.body)
        self.__e_scope()
        self.current_function = enclosing_type

    def visitVarStmt(self, var_: 'Var') -> None:
        self.__declare(var_.name)
        if var_.initializer:
            self.resolve_expression(var_.initializer)
        self.__define(var_.name)

    def visitReturnStmt(self, return_: 'ReturnStmt') -> None:
        if self.current_function == FunctionType.NONE:
            raise Exception("can't return in top level code.")

        if return_.value:
            self.resolve_expression(return_.value)

    def visitBlock(self, block_: 'Block') -> None:
        self.__b_scope()
        # begin scope
        self.resolve(block_.statements)
        # resolve
        # end scope
        self.__e_scope()

    def visitAssign(self, assign: 'Assign') -> object:
        self.resolve_expression(assign.expr)
        self.__resolve_local(assign, assign.name)

    def visitCall(self, call_: 'Call') -> object:
        self.resolve_expression(call_.callee)
        for arg in call_.args:
            self.resolve_expression(arg)

    def visitLogical(self, logical_: 'Logical') -> object:
        self.resolve_expression(logical_.left)
        self.resolve_expression(logical_.right)

    def visitBinary(self, binary: 'Binary') -> object:
        self.resolve_expression(binary.left)
        self.resolve_expression(binary.right)

    def visitUnary(self, unary: 'Unary') -> object:
        self.resolve_expression(unary.right)

    def visitFuncExpr(self, func_: 'FuncExpr') -> object:
        self.__b_scope()
        for arg in func_.args:
            self.__declare(arg)
            self.__define(arg)

        self.resolve(func_.stmts)
        self.__e_scope()

    def visitGrouping(self, grouping: 'Grouping') -> object:
        self.resolve_expression(grouping.expression)

    def visitLiteral(self, literal: 'Literal') -> object:
        return

    def visitVariable(self, variable: 'Variable') -> object:
        if len(self.scopes) != 0 and self.scopes[-1].get(variable.name.lexem) is False:
            raise Exception("Can't read local variable in its own initializer.")

        self.__resolve_local(variable, variable.name)

    def __b_scope(self) -> None:
        self.scopes.append({})

    def __e_scope(self) -> None:
        self.scopes.pop()

    def __declare(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return

        inner_most_scope = self.scopes[-1]
        if inner_most_scope.get(name.lexem) is not None:
            raise Exception(f'{name.lexem} already a variable with this name in this scope.')
        inner_most_scope[name.lexem] = False

    def __define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return

        inner_most_scope = self.scopes[-1]
        inner_most_scope[name.lexem] = True

    def __resolve_local(self, expr: 'Expr', name: Token) -> None:
        for i in range(1, len(self.scopes) + 1):
            scope = self.scopes[-i]
            if name.lexem in scope:
                self.interpreter.resolve(expr, i - 1)
                return
