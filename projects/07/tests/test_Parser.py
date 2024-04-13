import sys
sys.path.append("../")
from Parser import Parser 
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

    def __onelinePushPopCheck(self, operator, arg1, arg2):
        testLines = [f'{operator} {arg1} {arg2}']
        parser = Parser(testLines)
        parser.advance()
        assert parser.commandType() == CommandType.C_PUSH if operator == "push" else CommandType.C_POP
        assert parser.arg1() == arg1
        assert parser.arg2() == arg2
        assert parser.hasMoreLines() == False 
        
    def test_parsePushLocal(self):
        self.__onelinePushPopCheck("push", "local", 0)
    def test_parsePushArgument(self):
        self.__onelinePushPopCheck("push", "argument", 1)
    def test_parsePushThis(self):
        self.__onelinePushPopCheck("push", "this", 10)
    def test_parsePushThat(self):
        self.__onelinePushPopCheck("push", "that", 100)
    def test_parsePopConstant(self):
        self.__onelinePushPopCheck("pop", "constant", 1000)
    def test_parsePopStatic(self):
        self.__onelinePushPopCheck("pop", "static", 10000)
    def test_parsePopTemp(self):
        self.__onelinePushPopCheck("pop", "temp", 10)
    def test_parsePopPointer(self):
        self.__onelinePushPopCheck("pop", "pointer", 20)

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
    