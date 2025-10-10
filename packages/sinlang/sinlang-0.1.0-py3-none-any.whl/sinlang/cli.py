import sys
import os
from lark import Lark
from .interpreter import SinInterpreter

def load_parser():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    grammar_path = os.path.join(current_dir, 'sin_grammar.lark')
    
    with open(grammar_path, "r", encoding="utf-8") as f:
        sin_grammar = f.read()
    
    return Lark(sin_grammar, parser="lalr")

def run_sinlang_code(code, sin_parser, interpreter):
    try:
        tree = sin_parser.parse(code)
        interpreter.transform(tree)
    except Exception as e:
        print(f"Error: {e}")

def run_shell(sin_parser):
    print("--- SinLang Shell Mode ---")
    print("Enter 'exit' or 'quit' to end the session.")
    
    interpreter = SinInterpreter()

    while True:
        try:
            code = input("sin > ")
            if code.lower() in ['quit', 'exit']:
                break
            if not code.strip():
                continue
            
            run_sinlang_code(code, sin_parser, interpreter)
            
        except EOFError:
            break

def main():
    try:
        sin_parser = load_parser()
    except Exception as e:
        print(f"Fatal Error loading grammar: {e}")
        sys.exit(1)

    if len(sys.argv) == 1:
        run_shell(sin_parser)
    else:
        file_path = sys.argv[1]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                sin_code = f.read()
            print(f"--- Running SinLang file: {file_path} ---")
            run_sinlang_code(sin_code, sin_parser, SinInterpreter())
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"\n!!! SinLang Execution Error !!!\n{e}")

if __name__ == '__main__':
    main()
