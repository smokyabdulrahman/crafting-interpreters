from typing import TYPE_CHECKING, final

from src.ast.expr.visitor import Visitor as ExprVisitor
from src.ast.stmt.visitor import Visitor as StmtVisitor
from src.environment import Environment
from src.interperter_lib.exceptions import Return
from src.interperter_lib.native_lib.time import ClockFunc
from src.interperter_lib.schema import LoxAnonymousFunction, LoxCallable, LoxFunction
from src.tokens import TokenType

if TYPE_CHECKING:
    from src.ast.expr.schema import Assign, Binary, Call, Expr, FuncExpr, Grouping, Literal, Logical, Unary, Variable
    from src.ast.stmt.schema import Block, Expression, FuncStmt, IfStmt, Print, ReturnStmt, Stmt, Var, While


@final
class Interpreter(ExprVisitor[object], StmtVisitor[None]):
    globals = Environment()
    env = globals

    def __init__(self) -> None:
        self.globals.define('clock', ClockFunc())
        self.local: dict[object, int] = {}

    def interpret(self, statements: list['Stmt']) -> None:
        for statement in statements:
            self.execute(statement)

    def resolve(self, expr: 'Expr', i: int) -> None:
        self.local[expr] = i

    def execute(self, statement: 'Stmt') -> None:
        statement.accept(self)

    def executeBlock(self, statements: list['Stmt'], env: Environment) -> None:
        prev_env = self.env

        try:
            self.env = env
            for statement in statements:
                self.execute(statement)
        finally:
            self.env = prev_env

    def evaluate(self, expression: 'Expr') -> object:
        return expression.accept(self)

    def visitExpression(self, expression: 'Expression') -> None:
        self.evaluate(expression.expression)

    def visitWhile(self, while_: 'While') -> None:
        condition_result = self.evaluate(while_.condition)

        while self.__is_truth(condition_result):
            self.execute(while_.statement)
            condition_result = self.evaluate(while_.condition)

    def visitIfStmt(self, if_stmt_: 'IfStmt') -> None:
        condition_result = self.evaluate(if_stmt_.condition)

        if self.__is_truth(condition_result):
            self.execute(if_stmt_.then_branch)
        elif if_stmt_.else_branch:
            self.execute(if_stmt_.else_branch)

    def visitPrint(self, print_: 'Print') -> None:
        val = self.evaluate(print_.expression)
        print(f'{val}')

    def visitFuncStmt(self, func_: 'FuncStmt') -> None:
        func_definition = LoxFunction(func_, self.env)
        self.env.define(func_.name.lexem, func_definition)

    def visitVarStmt(self, var_: 'Var') -> None:
        value = None

        if var_.initializer:
            value = self.evaluate(var_.initializer)

        self.env.define(var_.name.lexem, value)

    def visitReturnStmt(self, return_: 'ReturnStmt') -> None:
        value: object | None = None

        if return_.value:
            value = self.evaluate(return_.value)

        raise Return(value)

    def visitBlock(self, block_: 'Block') -> None:
        self.executeBlock(block_.statements, Environment(enclosing=self.env))

    def visitAssign(self, assign: 'Assign') -> object:
        value = self.evaluate(assign.expr)
        lvl = self.local.get(assign)
        if lvl:
            self.env.assign_at(lvl, assign.name.lexem, value)
        else:
            self.env.assign(assign.name.lexem, value)

        return value

    def visitCall(self, call_: 'Call') -> object:
        callee = self.evaluate(call_.callee)
        args = []
        for expr in call_.args:
            args.append(self.evaluate(expr))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(f"this isn't a function to be called {call_.paren}")

        if len(args) != callee.arity():
            raise RuntimeError(f'Expected {callee.arity()} argumnets but got {len(args)}')

        return callee.call(self, args)

    def visitLogical(self, logical_: 'Logical') -> object:
        left_val = self.evaluate(logical_.left)
        left_is_truth = self.__is_truth(left_val)

        if logical_.operator.type == TokenType.OR:
            if left_is_truth:
                return left_val
        else:
            if not left_is_truth:
                return left_val

        return self.evaluate(logical_.right)

    def visitBinary(self, binary: 'Binary') -> object:
        left_val = self.evaluate(binary.left)
        right_val = self.evaluate(binary.right)

        # TODO: Allow for binary to work disregarding operands types
        # this might raise exceptions from python
        # look on how to define a standard for Lox
        match (binary.operator.type, left_val, right_val):
            case (TokenType.PLUS, str(), str()):
                return left_val + right_val
            case (TokenType.PLUS, float(), float()):
                return left_val + right_val
            case (TokenType.MINUS, float(), float()):
                return left_val - right_val
            case (TokenType.SLASH, float(), float()):
                return left_val / right_val
            case (TokenType.STAR, float(), float()):
                return left_val * right_val
            case (TokenType.LESS, float(), float()):
                return left_val < right_val
            case (TokenType.LESS, float(), float()):
                return left_val < right_val
            case (TokenType.LESS_EQUAL, float(), float()):
                return left_val <= right_val
            case (TokenType.GREATER, float(), float()):
                return left_val > right_val
            case (TokenType.GREATER_EQUAL, float(), float()):
                return left_val >= right_val
            case (TokenType.EQUAL_EQUAL, _, _):
                return self.__is_equal(left_val, right_val)
            case (TokenType.BANG_EQUAL, _, _):
                return not self.__is_equal(left_val, right_val)

        return None

    def visitUnary(self, unary: 'Unary') -> object:
        val = self.evaluate(unary.right)
        match unary.operator.type:
            case TokenType.MINUS:
                assert isinstance(val, float)
                return -float(val)
            case TokenType.BANG:
                return self.__is_truth(val)

        return None

    def visitFuncExpr(self, func_: 'FuncExpr') -> object:
        return LoxAnonymousFunction(func_, self.env)

    def visitGrouping(self, grouping: 'Grouping') -> object:
        return self.evaluate(grouping.expression)

    def visitLiteral(self, literal: 'Literal') -> object:
        return literal.value

    def visitVariable(self, variable: 'Variable') -> object:
        return self.lookup_var(variable)

    def lookup_var(self, variable: 'Variable') -> object:
        lvl = self.local.get(variable, None)
        if lvl is not None:
            return self.env.get_at(variable.name.lexem, lvl)
        return self.globals.get(variable.name.lexem)

    def __is_equal(self, left: object, right: object) -> bool:
        if not left and not right:
            return True
        if not left:
            return False

        return left == right

    def __is_truth(self, val: object) -> bool:
        if not val:
            return False
        if isinstance(val, bool):
            return val

        return True
