from HackVM import CommandType
import re

class ParserIllegalException(Exception):
    pass

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
    
    def hasMoreLines(self):
        if self.__currentLine < self.__numLines-1:
            return True
        else:
            return False
    
    def advance(self):
        self.__resetRes()
        while (self.hasMoreLines()):
            self.__currentLine += 1
            line = self.__lines[self.__currentLine]
            if self.__checkNoArg(line):
                break
            elif self.__checkOneArg(line):
                break
            elif self.__checkPushPop(line):
                break
            elif self.__checkFunctionCall(line):
                break
            elif self.__repatOnlyComment.fullmatch(line):
                continue
            else:
                raise ParserIllegalException(f'Illegal input line {self.__currentLine+1}: {line}')

    def commandType(self):
        return self.__commandType
    
    def arg1(self):
        return self.__arg1

    def arg2(self):
        return self.__arg2

    def __resetRes(self):
        self.__commandType = None
        self.__arg1 = ""
        self.__arg2 = -1
        
    def __defPatterns(self):
        self.__repatNoArg = re.compile(r'\s*(?P<operator>add|sub|neg|eq|gt|lt|and|or|not|return)\s*(//.*)?')
        hackSymbolPat = r'[a-zA-Z_\.\$\:][0-9a-zA-Z_\.\$\:]*'
        self.__repatOneArg = re.compile(r'\s*(?P<operator>label|goto|if-goto)\s+(?P<arg1>'+hackSymbolPat+r')\s*(//.*)?')
        self.__repatPushPop = re.compile(r'\s*(?P<operator>push|pop)\s+(?P<arg1>local|argument|this|that|constant|static|temp|pointer)\s+(?P<arg2>\d+)\s*(//.*)?')
        self.__repatFunctionCall = re.compile(r'\s*(?P<operator>function|call)\s+(?P<arg1>'+hackSymbolPat+r')\s+(?P<arg2>\d+)\s*(//.*)?')
        self.__repatOnlyComment = re.compile(r'\s*(//.*)?') # Including only white spaces

    def __checkNoArg(self, line):
        match = self.__repatNoArg.fullmatch(line) 
        if match == None:
            return False
        operator = match.group('operator')
        if operator == "return":
            self.__commandType = CommandType.C_RETURN
        else:
            self.__commandType = CommandType.C_ARITHMETIC
        self.__arg1 = operator
        return True
    
    def __checkOneArg(self, line):
        match = self.__repatOneArg.fullmatch(line) 
        if match == None:
            return False
        operator = match.group('operator')
        if operator == "label":
            self.__commandType = CommandType.C_LABEL
        elif operator == "goto":
            self.__commandType = CommandType.C_GOTO
        elif operator == "if-goto":
            self.__commandType = CommandType.C_IF
        self.__arg1 = match.group('arg1')
        return True
    
    def __checkPushPop(self, line):
        match = self.__repatPushPop.fullmatch(line) 
        if match == None:
            return False
        operator = match.group('operator')
        if operator == "push":
            self.__commandType = CommandType.C_PUSH
        elif operator == "pop":
            self.__commandType = CommandType.C_POP
        self.__arg1 = match.group('arg1')
        self.__arg2 = int(match.group('arg2'))
        return True
    
    def __checkFunctionCall(self, line):
        match = self.__repatFunctionCall.fullmatch(line) 
        if match == None:
            return False
        operator = match.group('operator')
        if operator == "function":
            self.__commandType = CommandType.C_FUNCTION
        elif operator == "call":
            self.__commandType = CommandType.C_CALL
        self.__arg1 = match.group('arg1')
        self.__arg2 = int(match.group('arg2'))
        return True
    
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
