import sys
import os
from Parser import Parser;
from CodeWriter import CodeWriter;
from HackVM import CommandType, SystemBootCodeFile

class VMTranslatorUnsupported(Exception):
    pass

class VMTranslator:
    def __init__(self, inFileNameOrdirName, outFileNameOroutCodeList):
        self.__inFileNameOrdirName = inFileNameOrdirName
        self.__outFileNameOroutCodeList = outFileNameOroutCodeList

    def translate(self):
        codeWriter = CodeWriter(self.__outFileNameOroutCodeList)
        for fileNameWithPath in self.__getVMFileListWithPath():
            print("Translating " + fileNameWithPath)
            codeWriter.setFileName(fileNameWithPath)
            self.__translateFile(fileNameWithPath, codeWriter)
            
        if isinstance(self.__outFileNameOroutCodeList, list):
            print("")
            print("\n".join(self.__outFileNameOroutCodeList))  
        else:
            # File mode
            codeWriter.close()

    def __translateFile(self, fileName, codeWriter):
        parser = Parser(fileName,1)
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
    
    def __getVMFileListWithPath(self):
        if os.path.isdir(self.__inFileNameOrdirName):
            # In case of directory path
            dirName = self.__inFileNameOrdirName
            listOfFilesAndDirs = os.listdir(dirName)
            # Get list of file names
            fileNames = [f for f in listOfFilesAndDirs if os.path.isfile(os.path.join(dirName, f))]
            # Filtering by file extenstion (.vm)
            vmFileList = [f for f in fileNames if f.endswith(".vm")]
            vmFileListWithPath = list(map(lambda f: os.path.join(dirName, f), vmFileList))
            # Bring "Sys.vm" to the top of the list
            sysBootCodeFile = os.path.join(dirName, SystemBootCodeFile)
            if sysBootCodeFile in vmFileListWithPath:
                return [sysBootCodeFile] + [x for x in vmFileListWithPath if x != sysBootCodeFile]
        else:
            return [self.__inFileNameOrdirName]
    

def main(argv):
    inFileNameOrdirName = argv[1]
    if len(argv) == 3:
        outFileNameOroutCodeList = argv[2]
    else:
        outFileNameOroutCodeList = []
    translator = VMTranslator(inFileNameOrdirName, outFileNameOroutCodeList)
    translator.translate()
    

if __name__ == '__main__':
    main(sys.argv)
