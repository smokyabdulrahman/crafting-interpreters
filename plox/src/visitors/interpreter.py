from typing import TYPE_CHECKING, final

from src.tokens import TokenType
from src.visitors.contract import Visitor

if TYPE_CHECKING:
    from src.ast.schema import Binary, Expr, Grouping, Literal, Unary


@final
class Interpreter(Visitor[object]):
    def interpret(self, expression: 'Expr') -> None:
        val = self.evaluate(expression)
        print(f'result: {val}')

    def evaluate(self, expression: 'Expr') -> object:
        return expression.accept(self)

    def visitBinary(self, binary: 'Binary') -> object:
        left_val = self.evaluate(binary.left)
        right_val = self.evaluate(binary.right)

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

    def visitGrouping(self, grouping: 'Grouping') -> object:
        return self.evaluate(grouping.expression)

    def visitLiteral(self, literal: 'Literal') -> object:
        return literal.value

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
