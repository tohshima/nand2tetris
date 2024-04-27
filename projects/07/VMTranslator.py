import sys
from Parser import Parser;
from CodeWriter import CodeWriter;
from HackVM import CommandType

class VMTranslatorUnsupported(Exception):
    pass

def main(argv):
    inFileName = argv[1]
    parser = Parser(inFileName,1)
    if len(argv) == 3:
        outFileName = argv[2]
        codeWriter = CodeWriter(outFileName)
    else:
        outCode = []
        codeWriter = CodeWriter(outCode)

    while parser.hasMoreLines():
        parser.advance()
        commandType = parser.commandType()
        if commandType == commandType.C_ARITHMETIC:
            codeWriter.writeArithmetic(parser.arg1())
        elif commandType == CommandType.C_PUSH or commandType == CommandType.C_POP:
            codeWriter.writePushPop(commandType, parser.arg1(), parser.arg2())
        elif commandType == CommandType.C_LABEL:
            codeWriter.writeLabel(parser.arg1())
        elif commandType == CommandType.C_GOTO:
            codeWriter.writeGoto(parser.arg1())
        elif commandType == CommandType.C_IF:
            codeWriter.writeIf(parser.arg1())
        elif commandType == CommandType.C_FUNCTION:
            codeWriter.writeFunction(parser.arg1(), parser.arg2())
        elif commandType == CommandType.C_RETURN:
            codeWriter.writeReturn()
        elif commandType == CommandType.C_CALL:
            codeWriter.writeCall(parser.arg1(), parser.arg2())
        else:
            raise VMTranslatorUnsupported(f'Unsupported command type: {commandType}.')
    
    if len(argv) == 3:
        codeWriter.close()
    else:
        print("")
        print("\n".join(outCode))  

if __name__ == '__main__':
    main(sys.argv)
