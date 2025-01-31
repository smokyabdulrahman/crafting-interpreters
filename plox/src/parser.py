from typing import final

from src.ast.expr.schema import Assign, Binary, Call, Expr, FuncExpr, Grouping, Literal, Logical, Unary, Variable
from src.ast.stmt.schema import Block, Expression, FuncStmt, IfStmt, Print, ReturnStmt, Stmt, Var, While
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
        if self.__match(TokenType.FUN):
            return self.fun_declaration()

        if self.__match(TokenType.VAR):
            return self.var_declaration()

        return self.statement()

    def statement(self) -> Stmt:
        if self.__match(TokenType.RETURN):
            return self.return_statment()
        if self.__match(TokenType.FOR):
            return self.for_statement()
        if self.__match(TokenType.WHILE):
            return self.while_statment()
        if self.__match(TokenType.IF):
            return self.if_statement()
        if self.__match(TokenType.PRINT):
            return self.print_statement()
        if self.__match(TokenType.BRACE_OPEN):
            statements = self.block()
            return Block(statements=statements)
        return self.expression_statement()

    def fun_declaration(self) -> Stmt:
        # fun token is already consumed
        name = self.__consume(TokenType.IDENTIFIER, 'Expect function name.')
        self.__consume(TokenType.PAREN_OPEN, 'Expected args list.')

        args: list[Token] = []
        if not self.__check(TokenType.PAREN_CLOSE):
            while True:
                if len(args) >= 255:
                    raise ParseError("Can't have more than 255 args.")
                args.append(self.__consume(TokenType.IDENTIFIER, 'Expected identifiers only.'))

                if not self.__match(TokenType.COMMA):
                    break

        self.__consume(TokenType.PAREN_CLOSE, "expected ')' to close fun call arguments list.")
        self.__consume(TokenType.BRACE_OPEN, "expected '{' to define fun body.")
        stmts = self.block()
        return FuncStmt(name=name, args=args, body=stmts)

    def var_declaration(self) -> Stmt:
        # var token is already consumed
        name = self.__consume(TokenType.IDENTIFIER, 'Expect varibale name.')

        initializer: Expr | None = None
        if self.__match(TokenType.EQUAL):
            initializer = self.expression()

        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Var(name=name, initializer=initializer)

    def return_statment(self) -> Stmt:
        # I need to check if i am in a function or not
        # How to know that we are in a function????

        # interpretation:
        # stop executing statments
        keyword = self.__previous()
        value: Expr | None = None
        if not self.__match(TokenType.SEMICOLON):
            value = self.expression()

        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")

        return ReturnStmt(keyword, value)

    def for_statement(self) -> Stmt:
        self.__consume(TokenType.PAREN_OPEN, "Expect '(' after 'while'.")
        initializer: Stmt | None = None
        if self.__match(TokenType.SEMICOLON):
            initializer = None
        elif self.__match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition: Expr | None = None
        if not self.__check(TokenType.SEMICOLON):
            condition = self.expression()
        self.__consume(TokenType.SEMICOLON, "expected ';' after 'while' condition.")

        increment: Expr | None = None
        if not self.__check(TokenType.PAREN_CLOSE):
            increment = self.expression()
        self.__consume(TokenType.PAREN_CLOSE, "expected ';' after 'while' increment.")

        body = self.statement()

        if increment:
            body = Block(statements=[body, Expression(increment)])

        if not condition:
            condition = Literal(True)

        body = While(condition, body)

        if initializer:
            body = Block(statements=[initializer, body])

        return body

    def while_statment(self) -> Stmt:
        self.__consume(TokenType.PAREN_OPEN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.__consume(TokenType.PAREN_CLOSE, "Expect ')' after 'while' condition.")
        while_statement_body = self.statement()

        return While(condition=condition, statement=while_statement_body)

    def if_statement(self) -> Stmt:
        self.__consume(TokenType.PAREN_OPEN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.__consume(TokenType.PAREN_CLOSE, "Expect ')' after 'if' condition.")
        then_branch = self.statement()
        if not self.__match(TokenType.ELSE):
            return IfStmt(condition=condition, then_branch=then_branch)

        else_branch = self.statement()
        return IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def print_statement(self) -> Stmt:
        expr = self.expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(expression=expr)

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.__check(TokenType.BRACE_CLOSE) and not self.__is_at_end():
            statements.append(self.declaration())

        self.__consume(TokenType.BRACE_CLOSE, "Block supposed to be closed with '}'")
        return statements

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Expression(expression=expr)

    def expression(self) -> Expr:
        # TODO:
        # handle FunctionExpression
        #
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.logical_or()

        if self.__match(TokenType.EQUAL):
            equals_token = self.__previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assign(name=expr.name, expr=value)

            raise ParseError(f'{equals_token} invalid assignment target.')

        return expr

    def logical_or(self) -> Expr:
        expr = self.logical_and()
        if self.__match(TokenType.OR):
            return Logical(
                left=expr,
                operator=self.__previous(),
                right=self.logical_and(),
            )

        return expr

    def logical_and(self) -> Expr:
        expr = self.equality()
        if self.__match(TokenType.AND):
            return Logical(
                left=expr,
                operator=self.__previous(),
                right=self.equality(),
            )

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

        return self.call()

    def call(self) -> Expr:
        expr = self.primary()

        while True:
            if self.__match(TokenType.PAREN_OPEN):
                expr = self.__finish_call(expr)
            else:
                break

        return expr

    def fun_expression(
        self,
    ) -> Expr:
        # fun token is already consumed
        # anonymous func, no identifer
        # name = self.__consume(TokenType.IDENTIFIER, 'Expect function name.')
        self.__consume(TokenType.PAREN_OPEN, 'Expected args list.')

        args: list[Token] = []
        if not self.__check(TokenType.PAREN_CLOSE):
            while True:
                if len(args) >= 255:
                    raise ParseError("Can't have more than 255 args.")
                args.append(self.__consume(TokenType.IDENTIFIER, 'Expected identifiers only.'))

                if not self.__match(TokenType.COMMA):
                    break

        self.__consume(TokenType.PAREN_CLOSE, "expected ')' to close fun call arguments list.")
        self.__consume(TokenType.BRACE_OPEN, "expected '{' to define fun body.")
        return FuncExpr(args=args, stmts=self.block())

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
            case TokenType.FUN:
                return self.fun_expression()
            case _:
                raise ParseError(f'{token}:{token.line} current token is invalid at this position')

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

    def __check(self, *token_types: TokenType) -> bool:
        # there might be a bug
        for token_type in token_types:
            if self.tokens[self.current].type == token_type:
                return True

        return False

    def __match(self, *token_types: TokenType) -> bool:
        res = self.__check(*token_types)

        if res:
            self.__advance()

        return res

    def __consume(self, token_type: TokenType, err_msg: str) -> Token:
        if not self.__match(token_type):
            raise ParseError(err_msg)

        return self.__previous()

    def __finish_call(self, callee: Expr) -> Expr:
        args: list[Expr] = []
        if not self.__check(TokenType.PAREN_CLOSE):
            while True:
                if len(args) >= 255:
                    raise ParseError("Can't have more than 255 args.")
                args.append(self.expression())

                if not self.__match(TokenType.COMMA):
                    break

        paren_close = self.__consume(TokenType.PAREN_CLOSE, "expected ')' to close fun call arguments list.")

        return Call(
            callee=callee,
            paren=paren_close,
            args=args,
        )
