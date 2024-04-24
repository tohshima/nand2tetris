import sys
sys.path.append("../")
from CodeWriter import CodeWriter 
from CommandType import CommandType

class TestCase:

    def setup_method(self,method):
        pass

    def teardownn_method(self,method):
        pass

    def test_PushConstant(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_PUSH, "constant", 7)
        print("")
        print("\n".join(outlines))
        assert writer.pc == 8

    def test_PushArgument(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_PUSH, "argument", 7)
        print("")
        print("\n".join(outlines))
        assert writer.pc == 11

    def test_PopConstant(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_POP, "constant", 7)
        print("")
        print("\n".join(outlines))
        assert writer.pc == 2

    def test_PopArgument(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_POP, "argument", 7)
        print("")
        print("\n".join(outlines))
        assert writer.pc == 14

    def test_PopTemp(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_POP, "temp", 7)
        print("")
        print("\n".join(outlines))
        assert writer.pc == 14

    def test_Add(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writeArithmetic("add")
        print("")
        print("\n".join(outlines))
        assert writer.pc == 9

    def test_Sub(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writeArithmetic("sub")
        print("")
        print("\n".join(outlines))
        assert writer.pc == 9

    def test_SimpleAdd(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_PUSH, "constant", 7)
        writer.writePushPop(CommandType.C_PUSH, "constant", 8)
        writer.writeArithmetic("add")
        print("")
        print("\n".join(outlines))
        assert writer.pc == 25

    def test_SimpleAddToFile(self):
        outlines = []
        writer = CodeWriter("testFiles/SimpleAdd.asm")
        writer.writePushPop(CommandType.C_PUSH, "constant", 7)
        writer.writePushPop(CommandType.C_PUSH, "constant", 8)
        writer.writeArithmetic("add")

    def test_Or(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_PUSH, "constant", 1)
        writer.writePushPop(CommandType.C_PUSH, "constant", 0)
        writer.writeArithmetic("or")
        print("")
        print("\n".join(outlines))
        assert writer.pc == 25

    def test_Eq(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_PUSH, "constant", 1)
        writer.writePushPop(CommandType.C_PUSH, "constant", 0)
        writer.writeArithmetic("eq")
        print("")
        print("\n".join(outlines))
        assert writer.pc == 35

    def test_Gt(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_PUSH, "constant", 1)
        writer.writePushPop(CommandType.C_PUSH, "constant", 0)
        writer.writeArithmetic("gt")
        print("")
        print("\n".join(outlines))
        assert writer.pc == 35

    def test_Lt(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop(CommandType.C_PUSH, "constant", 1)
        writer.writePushPop(CommandType.C_PUSH, "constant", 0)
        writer.writeArithmetic("lt")
        print("")
        print("\n".join(outlines))
        assert writer.pc == 35

