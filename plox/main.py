import sys

from src.scanner import Scanner

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        raise ValueError('you can only provide a file for now')

    with open(argv[1], 'r') as f:
        scanner = Scanner(f.read())
        print(scanner.scan_tokens())
