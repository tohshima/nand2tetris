import sys
from Parser import Parser;
from CodeWriter import CodeWriter;

def main(argv):
    inFileName = argv[1]
    outFileName = argv[2]
    parser = Parser(inFileName,1)
    codeWriter = CodeWriter(outFileName)

if __name__ == '__main__':
    main(sys.argv)
