from string import ascii_letters

from src.tokens import Token, TokenType


class Scanner:
    def __init__(
        self,
        source: str,
    ) -> None:
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self._keywords = {
            'and': TokenType.AND,
            'class': TokenType.CLASS,
            'else': TokenType.ELSE,
            'false': TokenType.FALSE,
            'for': TokenType.FOR,
            'fun': TokenType.FUN,
            'if': TokenType.IF,
            'nil': TokenType.NIL,
            'or': TokenType.OR,
            'print': TokenType.PRINT,
            'return': TokenType.RETURN,
            'super': TokenType.SUPER,
            'this': TokenType.THIS,
            'true': TokenType.TRUE,
            'var': TokenType.VAR,
            'while': TokenType.WHILE,
        }

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(
            Token(
                type=TokenType.EOF,
                lexem='',
                literal=None,
                line=self.line,
            )
        )

        return self.tokens

    def scan_token(self) -> None:  # noqa: C901
        c = self.advance()
        match c:
            case x if self.is_alpha(c):
                self.identifier()
            case x if x.isdigit():
                self.number()
            case '"':
                self.string()
            case '/':
                # skip if it's a comment
                if self.match('/'):
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                elif self.match('*'):
                    # multiline comment
                    while not (self.peek() == '*' and self.peek_next() == '/') and not self.is_at_end():
                        if self.peek() == '\n':
                            self.line += 1
                        self.advance()

                    if self.is_at_end():
                        raise ValueError('non terminal multiline comment')

                    # consume closing comment tag
                    self.advance()
                    self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case '=':
                if self.match('='):
                    self.add_token(TokenType.EQUAL_EQUAL)
                else:
                    self.add_token(TokenType.EQUAL)
            case '<':
                if self.match('='):
                    self.add_token(TokenType.LESS_EQUAL)
                else:
                    self.add_token(TokenType.LESS)
            case '>':
                if self.match('='):
                    self.add_token(TokenType.GREATER_EQUAL)
                else:
                    self.add_token(TokenType.GREATER)
            case '!':
                if self.match('='):
                    self.add_token(TokenType.BANG_EQUAL)
                else:
                    self.add_token(TokenType.BANG)
            case '+':
                self.add_token(TokenType.PLUS)
            case '-':
                self.add_token(TokenType.MINUS)
            case '*':
                self.add_token(TokenType.STAR)
            case ';':
                self.add_token(TokenType.SEMICOLON)
            case ',':
                self.add_token(TokenType.COMMA)
            case '(':
                self.add_token(TokenType.PAREN_OPEN)
            case ')':
                self.add_token(TokenType.PAREN_CLOSE)
            case '{':
                self.add_token(TokenType.BRACE_OPEN)
            case '}':
                self.add_token(TokenType.BRACE_CLOSE)
            case ' ' | '\r' | '\t':
                return
            case '\n':
                self.line += 1
            case _:
                # fix this later to add the error somewhere and not break
                raise ValueError(f'line {self.line}: Unexpected character -> {repr(c)}')

    def match(self, match_c: str) -> bool:
        next_c = self.peek()
        if next_c != match_c:
            return False

        self.current += 1

        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'

        c = self.source[self.current : self.current + 1]
        return ''.join(c)

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'

        c = self.source[self.current + 1 : self.current + 2]
        return ''.join(c)

    def advance(self) -> str:
        c = self.source[self.current : self.current + 1]
        self.current += 1

        return ''.join(c)

    def add_token(self, token_type: TokenType) -> None:
        self.tokens.append(
            Token(
                type=token_type,
                lexem=''.join(self.source[self.start : self.current]),
                literal=None,
                line=self.line,
            )
        )

    def add_token_w_value(self, token_type: TokenType, value: str) -> None:
        self.tokens.append(
            Token(
                type=token_type,
                lexem=value,
                literal=None,
                line=self.line,
            )
        )

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise ValueError('Non terminal string')

        # we reached a '"' now
        self.advance()
        self.add_token_w_value(
            TokenType.STRING,
            ''.join(self.source[self.start + 1 : self.current - 1]),
        )

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        # handle fraction part
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # consume .

            while self.peek().isdigit():
                self.advance()

        self.add_token_w_value(
            TokenType.NUMBER,
            ''.join(self.source[self.start : self.current]),
        )

    def identifier(self) -> None:
        while self.is_alpha(self.peek()):
            self.advance()

        type = self._keywords.get(self.source[self.start : self.current], TokenType.IDENTIFIER)
        self.add_token(type)

    def is_alpha(self, char: str) -> bool:
        if char in ascii_letters or char == '_':
            return True

        return False
