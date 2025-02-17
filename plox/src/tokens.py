from dataclasses import dataclass
from enum import StrEnum, auto


class TokenType(StrEnum):
    # single char tokens
    ## arthmatic
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ## M
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()
    ## grouping
    BRACE_OPEN = auto()
    BRACE_CLOSE = auto()
    PAREN_OPEN = auto()
    PAREN_CLOSE = auto()

    # 1-2 char tokens
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords, used in the language
    AND = auto()
    IF = auto()
    ELSE = auto()
    TRUE = auto()
    FALSE = auto()
    CLASS = auto()
    FOR = auto()
    FUN = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    VAR = auto()
    WHILE = auto()

    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexem: str
    literal: object
    line: int

    def __str__(self) -> str:
        return f'[{self.type}]({self.lexem})'
