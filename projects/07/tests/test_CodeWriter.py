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
        writer.writePushPop("push", "constant", 7)
        print("")
        print("\n".join(outlines))

    def test_PushArgument(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop("push", "argument", 7)
        print("")
        print("\n".join(outlines))

    def test_Add(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writeArithmetic("add")
        print("")
        print("\n".join(outlines))

    def test_Sub(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writeArithmetic("sub")
        print("")
        print("\n".join(outlines))

    def test_SimpleAdd(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop("push", "constant", 7)
        writer.writePushPop("push", "constant", 8)
        writer.writeArithmetic("add")
        print("")
        print("\n".join(outlines))

    def test_SimpleAddToFile(self):
        outlines = []
        writer = CodeWriter("testFiles/SimpleAdd.asm")
        writer.writePushPop("push", "constant", 7)
        writer.writePushPop("push", "constant", 8)
        writer.writeArithmetic("add")

    def test_Or(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop("push", "constant", 1)
        writer.writePushPop("push", "constant", 0)
        writer.writeArithmetic("or")
        print("")
        print("\n".join(outlines))

    def test_Eq(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop("push", "constant", 1)
        writer.writePushPop("push", "constant", 0)
        writer.writeArithmetic("eq")
        print("")
        print("\n".join(outlines))

    def test_Gt(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop("push", "constant", 1)
        writer.writePushPop("push", "constant", 0)
        writer.writeArithmetic("gt")
        print("")
        print("\n".join(outlines))

    def test_Lt(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writePushPop("push", "constant", 1)
        writer.writePushPop("push", "constant", 0)
        writer.writeArithmetic("lt")
        print("")
        print("\n".join(outlines))

