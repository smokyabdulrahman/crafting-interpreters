import sys

from src.interperter_lib.interpreter import Interpreter
from src.parser import Parser
from src.resolver import Resolver
from src.scanner import Scanner
from src.visitors.ast_printer import AstPrinter

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        raise ValueError('you can only provide a file for now')

    with open(argv[1], 'r') as f:
        scanner = Scanner(f.read())
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()

        if not statements:
            raise ValueError('Dude, something went wrong')

        print(AstPrinter().print(statements))
        interpreter = Interpreter()
        resolver = Resolver(interpreter)
        resolver.resolve(statements)
        interpreter.interpret(statements)
