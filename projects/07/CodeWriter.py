from CommandType import CommandType

class CodeWriter:
    def __init__(self, filename_or_testLines, debug=0):
        self.__debug = debug

        self.__writeToList = False
        self.__filename_or_testLines = filename_or_testLines

        if isinstance(filename_or_testLines, list):
            self.__writeToList = True
        else:
            self.__f = open(filename_or_testLines, "w")

    def __makeAddCode(self):
        code = []
        code.append("add1")
        code.append("add2")
        return code

    def writeArithmetic(self, command):
        if command == "add":
            code = self.__makeAddCode()
        if self.__writeToList:
            self.__filename_or_testLines.extend(code)           
        else:
            self.__f.write("\n".join(code))

    def close(self):
        self.__f.close()

    