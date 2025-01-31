from typing import TYPE_CHECKING, final

from src.ast.expr.visitor import Visitor as ExprVisitor
from src.ast.stmt.schema import Block
from src.ast.stmt.visitor import Visitor as StmtVistior

if TYPE_CHECKING:
    from src.ast.expr.schema import Assign, Binary, Call, Expr, FuncExpr, Grouping, Literal, Logical, Unary, Variable
    from src.ast.stmt.schema import Expression, FuncStmt, IfStmt, Print, ReturnStmt, Stmt, Var, While


@final
class AstPrinter(ExprVisitor[str], StmtVistior[str]):
    def print(self, statements: list['Stmt']) -> str:
        output = ''
        for stmt in statements:
            output += stmt.accept(self)
        return output

    def parenthesize(self, name: str, *exprs: 'Expr') -> str:
        output = f'({name}'
        for expr in exprs:
            output += f' {expr.accept(self)}'
        output += ')'

        return output

    def print_block(self, stmts: list['Stmt']) -> str:
        output = '(block'
        for stmt in stmts:
            output += f' {stmt.accept(self)}'
        output += ')'

        return output

    def visitExpression(self, expression: 'Expression') -> str:
        return expression.expression.accept(self)

    def visitWhile(self, while_: 'While') -> str:
        return f'(while {while_.condition.accept(self)} {while_.statement.accept(self)})'

    def visitIfStmt(self, if_stmt_: 'IfStmt') -> str:
        output = '(if '
        output += if_stmt_.condition.accept(self)
        output += ' then '
        output += if_stmt_.then_branch.accept(self)

        if if_stmt_.else_branch:
            output += ' else '
            output += if_stmt_.else_branch.accept(self)

        return output

    def visitPrint(self, print_: 'Print') -> str:
        return self.parenthesize('print', print_.expression)

    def visitFuncStmt(self, func_: 'FuncStmt') -> str:
        return f'fun({func_.name.lexem} {self.print_block(func_.body)})'

    def visitReturnStmt(self, return_: 'ReturnStmt') -> str:
        if return_.value:
            return self.parenthesize('return', return_.value)

        return 'return nil'

    def visitVarStmt(self, var_: 'Var') -> str:
        if not var_.initializer:
            return f'(define_var {var_.name.lexem} )'

        return self.parenthesize(f'define_var({var_.name.lexem})', var_.initializer)

    def visitBlock(self, block_: 'Block') -> str:
        return self.print_block(block_.statements)

    def visitAssign(self, assign: 'Assign') -> str:
        return self.parenthesize(f'assign_var({assign.name.lexem})', assign.expr)

    def visitCall(self, call_: 'Call') -> str:
        return self.parenthesize('call', call_.callee)

    def visitLogical(self, logical_: 'Logical') -> str:
        return f'{logical_.left.accept(self)} {logical_.operator.type} {logical_.right.accept(self)}'

    def visitBinary(self, binary: 'Binary') -> str:
        return self.parenthesize(binary.operator.lexem, binary.left, binary.right)

    def visitUnary(self, unary: 'Unary') -> str:
        return self.parenthesize(unary.operator.lexem, unary.right)

    def visitFuncExpr(self, func_: 'FuncExpr') -> str:
        return f'anonymous_fun({self.print_block(func_.stmts)})'

    def visitGrouping(self, grouping: 'Grouping') -> str:
        return self.parenthesize('group', grouping.expression)

    def visitLiteral(self, literal: 'Literal') -> str:
        if literal.value is None:
            return 'nil'

        return f'{literal.value}'

    def visitVariable(self, variable: 'Variable') -> str:
        return f'{variable.name.lexem}'
