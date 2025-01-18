from typing import final

from src.ast.expr.schema import Assign, Binary, Expr, Grouping, Literal, Unary, Variable
from src.ast.stmt.schema import Expression, Print, Stmt, Var
from src.tokens import Token, TokenType


@final
class ParseError(RuntimeError): ...


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Stmt] | None:
        try:
            statements: list[Stmt] = []
            while not self.__is_at_end():
                statements.append(self.declaration())

            return statements
        except ParseError as e:
            # For now, later we are going to handle the exception by syncronizing
            print(
                'aaaa',
                e,
            )
            return None

    def declaration(self) -> Stmt:
        if self.__match(TokenType.VAR):
            return self.var_declaration()

        return self.statement()

    def statement(self) -> Stmt:
        if self.__match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def var_declaration(self) -> Stmt:
        # var token is already consumed
        name = self.__consume(TokenType.IDENTIFIER, 'Expect varibale name.')

        initializer: Expr | None = None
        if self.__match(TokenType.EQUAL):
            initializer = self.expression()

        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Var(name=name, initializer=initializer)

    def print_statement(self) -> Stmt:
        expr = self.expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(expression=expr)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Expression(expression=expr)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.equality()

        if self.__match(TokenType.EQUAL):
            equals_token = self.__previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assign(name=expr.name, expr=value)

            raise ParseError(f'{equals_token} invalid assignment target.')

        return expr

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
            case TokenType.STRING:
                return Literal(value=token.lexem)
            case TokenType.NUMBER:
                return Literal(value=float(token.lexem))
            case TokenType.IDENTIFIER:
                return Variable(name=token)
            case TokenType.TRUE:
                return Literal(value=True)
            case TokenType.FALSE:
                return Literal(value=False)
            case TokenType.NIL:
                return Literal(value=None)
            case TokenType.PAREN_OPEN:
                expr = self.expression()
                self.__consume(TokenType.PAREN_CLOSE, 'no grouping PAREN_CLOSE')

                return Grouping(expression=expr)
            case _:
                raise ParseError(f'{token} current token is invalid at this position')

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

    def __consume(self, token_type: TokenType, err_msg: str) -> Token:
        if not self.__match(token_type):
            raise ParseError(err_msg)

        return self.__previous()
