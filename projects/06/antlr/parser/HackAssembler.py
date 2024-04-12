import sys
from antlr4 import *
from hackasmLexer import hackasmLexer
from hackasmParser import hackasmParser
from myHackasmListener import myHackasmListener

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = hackasmLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = hackasmParser(stream)
    tree = parser.hackasm()
    if parser.getNumberOfSyntaxErrors() > 0:
        print("syntax errors")
    else:
        listener = myHackasmListener()
        walker = ParseTreeWalker()
        walker.walk(listener, tree)

if __name__ == '__main__':
    main(sys.argv)
