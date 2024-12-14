from src.ast.schema import Binary, Grouping, Literal, Unary
from src.tokens import Token, TokenType
from src.visitors.ast_printer import AstPrinter

if __name__ == '__main__':
    ast_printer = AstPrinter()
    tree = Binary(
        left=Grouping(
            Binary(
                left=Literal(value=3),
                operator=Token(
                    type=TokenType.STAR,
                    lexem='*',
                    literal=None,
                    line=1,
                ),
                right=Unary(
                    operator=Token(
                        type=TokenType.MINUS,
                        lexem='-',
                        literal=None,
                        line=1,
                    ),
                    right=Literal(value=2),
                ),
            )
        ),
        operator=Token(type=TokenType.STAR, lexem='*', literal=None, line=1),
        right=Literal(value=10),
    )

    print(ast_printer.print(tree))
