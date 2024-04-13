from CommandType import CommandType
import re

class Parser:
    def __init__(self, filename_or_testLines, debug=0):
        self.__debug = debug

        self.__currentLine = -1
        self.__resetRes()

        if isinstance(filename_or_testLines, list):
            self.__lines = filename_or_testLines
        else:
            with open(filename_or_testLines, "r") as f:
                self.__lines = f.read().splitlines()        
        self.__numLines = len(self.__lines)

        self.__defPatterns()
    
    def __resetRes(self):
        self.__commandType = None
        self.__arg1 = ""
        self.__arg2 = -1
        
    def __defPatterns(self):
        self.__repatArithmetic = re.compile(r'\s*(?P<operator>add|sub|neg|eq|gt|lt|and|or|not)\s*(//.*)?')
        self.__repatPushPop = re.compile(r'\s*(?P<operator>push|pop)\s+(?P<arg1>local|argument|this|that|constant|static|temp|pointer)\s+(?P<arg2>\d+)\s*(//.*)?')
        self.__repatOnlyComment = re.compile(r'\s*(//.*)?') # Including only white spaces

    def hasMoreLines(self):
        if self.__currentLine < self.__numLines-1:
            return True
        else:
            return False
    
    def __checkArithmetic(self, line):
        match = self.__repatArithmetic.fullmatch(line) 
        if match == None:
            return False
        self.__commandType = CommandType.C_ARITHMETIC
        self.__arg1 = match.group('operator')
        return True
    
    def __checkPushPop(self, line):
        match = self.__repatPushPop.fullmatch(line) 
        if match == None:
            return False
        mg1 = match.group('operator')
        if mg1 == "push":
            self.__commandType = CommandType.C_PUSH
        elif mg1 == "pop":
            self.__commandType = CommandType.C_POP
        self.__arg1 = match.group('arg1')
        self.__arg2 = int(match.group('arg2'))
        return True
    
    def advance(self):
        while (self.hasMoreLines()):
            self.__currentLine += 1
            self.__resetRes()

            line = self.__lines[self.__currentLine]
            if self.__checkArithmetic(line):
                break
            elif self.__checkPushPop(line):
                break
            elif self.__repatOnlyComment.fullmatch(line):
                continue
            else:
                raise Exception(f'Illegal input line {self.__currentLine+1}: {line}')

    def commandType(self):
        return self.__commandType
    
    def arg1(self):
        return self.__arg1

    def arg2(self):
        return self.__arg2

    # for unit test
    @property
    def currentLine(self):
        return self.__currentLine
    
    @property
    def numLines(self):
        return self.__numLines
    
    @property
    def lines(self):
        return self.__lines
