from typing import final

from src.ast.schema import Binary, Expr, Grouping, Literal, Unary
from src.tokens import Token, TokenType


@final
class ParseError(RuntimeError): ...


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Expr | None:
        try:
            return self.expression()
        except ParseError:
            # For now, later we are going to handle the exception by syncronizing
            return None

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.__match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.__previous()
            right = self.comparison()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.__match(TokenType.MINUS, TokenType.PLUS):
            op = self.__previous()
            right = self.term()
            expr = Binary(left=expr, operator=op, right=right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.__match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            op = self.__previous()
            right = self.factor()
            expr = Binary(left=expr, operator=op, right=right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.__match(TokenType.SLASH, TokenType.STAR):
            op = self.__previous()
            right = self.unary()
            expr = Binary(left=expr, operator=op, right=right)

        return expr

    def unary(self) -> Expr:
        if self.__match(TokenType.BANG, TokenType.MINUS):
            return Unary(
                operator=self.__previous(),
                right=self.unary(),
            )

        return self.primary()

    def primary(self) -> Expr:
        token = self.__advance()
        match token.type:
            case TokenType.NUMBER:
                return Literal(value=float(token.lexem))
            case TokenType.IDENTIFIER:
                return Literal(value=token.lexem)
            case TokenType.TRUE:
                return Literal(value=True)
            case TokenType.FALSE:
                return Literal(value=False)
            case TokenType.NIL:
                return Literal(value=None)
            case TokenType.PAREN_OPEN:
                expr = self.expression()
                if not self.__match(TokenType.PAREN_CLOSE):
                    raise ParseError('no grouping PAREN_CLOSE')
                return Grouping(expression=expr)
            case _:
                raise ParseError('current token is invalid at this position')

    def __previous(self) -> Token:
        return self.tokens[self.current - 1]

    def __peek(self) -> Token:
        return self.tokens[self.current]

    def __advance(self) -> Token:
        if not self.__is_at_end():
            self.current += 1

        return self.__previous()

    def __is_at_end(self) -> bool:
        return self.__peek().type == TokenType.EOF

    def __match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.tokens[self.current].type == token_type:
                self.__advance()
                return True

        return False
