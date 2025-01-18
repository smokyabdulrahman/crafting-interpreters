from typing import TYPE_CHECKING, final

from src.ast.expr.visitor import Visitor as ExprVisitor
from src.ast.stmt.visitor import Visitor as StmtVistior

if TYPE_CHECKING:
    from src.ast.expr.schema import Binary, Expr, Grouping, Literal, Unary
    from src.ast.stmt.schema import Stmt, Expression, Print


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

    def visitExpression(self, expression: 'Expression') -> str:
        return expression.expression.accept(self)

    def visitPrint(self, print_: 'Print') -> str:
        return self.parenthesize('print', print_.expression)

    def visitBinary(self, binary: 'Binary') -> str:
        return self.parenthesize(binary.operator.lexem, binary.left, binary.right)

    def visitUnary(self, unary: 'Unary') -> str:
        return self.parenthesize(unary.operator.lexem, unary.right)

    def visitGrouping(self, grouping: 'Grouping') -> str:
        return self.parenthesize('group', grouping.expression)

    def visitLiteral(self, literal: 'Literal') -> str:
        if literal.value is None:
            return 'nil'

        return f'{literal.value}'
