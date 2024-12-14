from typing import TYPE_CHECKING, final

from src.visitors.contract import Visitor

if TYPE_CHECKING:
    from src.ast.schema import Binary, Expr, Grouping, Literal, Unary


@final
class AstPrinter(Visitor[str]):
    def print(self, expr: 'Expr') -> str:
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs: 'Expr') -> str:
        output = f'({name}'
        for expr in exprs:
            output += f' {expr.accept(self)}'
        output += ')'

        return output

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
