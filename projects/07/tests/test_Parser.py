import sys
sys.path.append("../")
from Parser import Parser 
from Parser import ParserIllegalException
from CommandType import CommandType

class TestCase:

    def setup_method(self,method):
        pass

    def teardownn_method(self,method):
        pass

    def test_oneLineFile(self):
        parser = Parser("testFiles/oneLineFile.vm")
        assert parser.currentLine == -1
        assert parser.numLines == 1
        assert parser.lines[0] == "// This is an one line file."    

    def test_oneLineWithNewlineFile(self):
        parser = Parser("testFiles/oneLineWithNewLineFile.vm")
        assert parser.currentLine == -1
        assert parser.numLines == 1
        assert parser.lines[0] == "// This is an one line with new line file."    

    def test_twoLineWithNewlineFile(self):
        parser = Parser("testFiles/twoLinesWithNewLineFile.vm")
        assert parser.currentLine == -1
        assert parser.numLines == 2
        assert parser.lines[0] == "// line 1."    
        assert parser.lines[1] == "// line 2."   
        assert parser.hasMoreLines() == True 

        parser.advance()
        assert parser.hasMoreLines() == False
        assert parser.currentLine == 1

    def __onelineArithmeticCheck(self, key):
        testLines = [key]
        parser = Parser(testLines)
        assert parser.currentLine == -1
        assert parser.numLines == 1
        parser.advance()
        assert parser.commandType() == CommandType.C_ARITHMETIC
        assert parser.arg1() == key
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == False 

    def test_parseAdd(self):
        self.__onelineArithmeticCheck("add")

    def test_parseAddInComment(self):
        testLines = ["  // add"]
        parser = Parser(testLines)
        parser.advance()
        assert parser.commandType() == None
        assert parser.arg1() == ""
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == False 

    def test_parseAddAndComment(self):
        testLines = [" add  //"]
        parser = Parser(testLines)
        parser.advance()
        assert parser.commandType() == CommandType.C_ARITHMETIC
        assert parser.arg1() == "add"
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == False 

    def test_parseSub(self):
        self.__onelineArithmeticCheck("sub")
    def test_parseNeg(self):
        self.__onelineArithmeticCheck("neg")
    def test_parseEq(self):
        self.__onelineArithmeticCheck("eq")
    def test_parseGt(self):
        self.__onelineArithmeticCheck("gt")
    def test_parseLt(self):
        self.__onelineArithmeticCheck("lt")
    def test_parseAnd(self):
        self.__onelineArithmeticCheck("and")
    def test_parseOr(self):
        self.__onelineArithmeticCheck("or")
    def test_parseNot(self):
        self.__onelineArithmeticCheck("not")

    def test_parseArithmeticMulti(self):
        testLines = ["add "," ","   // ", "   not   // a"]
        parser = Parser(testLines)
        assert parser.numLines == 4
        parser.advance()
        assert parser.commandType() == CommandType.C_ARITHMETIC
        assert parser.arg1() == "add"
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == True 
        parser.advance()
        assert parser.commandType() == CommandType.C_ARITHMETIC
        assert parser.arg1() == "not"
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == False 

    def test_parseReturn(self):
        testLines = ["return"]
        parser = Parser(testLines)
        parser.advance()
        assert parser.commandType() == CommandType.C_RETURN
        assert parser.arg1() == "return"
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == False 

    def __onelineOneArgCheck(self, operator, arg1):
        testLines = [f'{operator} {arg1}']
        parser = Parser(testLines)
        parser.advance()
        if operator == "label":
            commandType = CommandType.C_LABEL
        elif operator == "goto":
            commandType = CommandType.C_GOTO
        elif operator == "if-goto":
            commandType = CommandType.C_IF
        assert parser.commandType() == commandType
        assert parser.arg1() == arg1
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == False 

    def test_parseLabel(self):
        self.__onelineOneArgCheck("label", "AA_BB.CC")

    def test_parseGoto(self):
        self.__onelineOneArgCheck("goto", "abcd")

    def test_parseIfGoto(self):
        self.__onelineOneArgCheck("if-goto", "$")

    def __onelineTwoArgsCheck(self, operator, arg1, arg2):
        testLines = [f'{operator} {arg1} {arg2}']
        parser = Parser(testLines)
        parser.advance()
        if operator == "push":
            commandType = CommandType.C_PUSH
        elif operator == "pop":
            commandType = CommandType.C_POP
        elif operator == "function":
            commandType = CommandType.C_FUNCTION
        elif operator == "call":
            commandType = CommandType.C_CALL
        assert parser.commandType() == commandType
        assert parser.arg1() == arg1
        assert parser.arg2() == arg2
        assert parser.hasMoreLines() == False 
        
    def test_parsePushLocal(self):
        self.__onelineTwoArgsCheck("push", "local", 0)
    def test_parsePushArgument(self):
        self.__onelineTwoArgsCheck("push", "argument", 1)
    def test_parsePushThis(self):
        self.__onelineTwoArgsCheck("push", "this", 10)
    def test_parsePushThat(self):
        self.__onelineTwoArgsCheck("push", "that", 100)
    def test_parsePopConstant(self):
        self.__onelineTwoArgsCheck("pop", "constant", 1000)
    def test_parsePopStatic(self):
        self.__onelineTwoArgsCheck("pop", "static", 10000)
    def test_parsePopTemp(self):
        self.__onelineTwoArgsCheck("pop", "temp", 10)
    def test_parsePopPointer(self):
        self.__onelineTwoArgsCheck("pop", "pointer", 20)

    def test_parsePopPointerWithComment(self):
        testLines = ["  pop  pointer 2  // pop"]
        parser = Parser(testLines)
        parser.advance()
        assert parser.commandType() == CommandType.C_POP
        assert parser.arg1() == "pointer"
        assert parser.arg2() == 2
        assert parser.hasMoreLines() == False 

    def test_parsePopPointerInComment(self):
        testLines = ["//  pop  pointer 2  // pop"]
        parser = Parser(testLines)
        parser.advance()
        assert parser.commandType() == None
        assert parser.arg1() == ""
        assert parser.arg2() == -1
        assert parser.hasMoreLines() == False 

    def test_parseFunction(self):
        self.__onelineTwoArgsCheck("function", "local", 1234)

    def test_parseCall(self):
        self.__onelineTwoArgsCheck("call", "_:.$12AA_bb", 12345)

    def test_parseCallWithIllegalSymbol(self):
        try:
            self.__onelineTwoArgsCheck("call", "0_:.$12", 12345)
        except ParserIllegalException:
            assert True
        else:
            assert False

    def test_MemoryAccessBasicTest(self):
        parser = Parser("../StackArithmetic/SimpleAdd/SimpleAdd.vm")
        assert parser.numLines == 9
        parser.advance()
        assert parser.commandType() == CommandType.C_PUSH
        assert parser.arg1() == "constant"
        assert parser.arg2() == 7
        assert parser.currentLine == 6 
        assert parser.hasMoreLines() == True 
        parser.advance()
        assert parser.commandType() == CommandType.C_PUSH
        assert parser.arg1() == "constant"
        assert parser.arg2() == 8
        assert parser.currentLine == 7 
        assert parser.hasMoreLines() == True 
        parser.advance()
        assert parser.commandType() == CommandType.C_ARITHMETIC
        assert parser.arg1() == "add"
        assert parser.arg2() == -1
        assert parser.currentLine == 8 
        assert parser.hasMoreLines() == False 
        parser.advance()
        assert parser.commandType() == None
        assert parser.arg1() == ""
        assert parser.arg2() == -1
        assert parser.currentLine == 8 
        assert parser.hasMoreLines() == False 


    